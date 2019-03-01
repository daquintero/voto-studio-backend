import json

from django.apps import apps
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db import IntegrityError
from django.db.models.fields.related import OneToOneRel, ManyToOneRel, ManyToManyRel
from django.shortcuts import get_object_or_404
from rest_framework import authentication, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from shared.api.parsers import camel_to_underscore, underscore_to_camel
from shared.utils import get_model, create_slice
from . import serializers
from voto_studio_backend.changes.models import Change, get_rels_dict_default
from voto_studio_backend.media.models import Image, Video, Resource
from voto_studio_backend.media.serializers import ImageSerializer, VideoSerializer, ResourceSerializer
from voto_studio_backend.permissions.shortcuts import get_object_or_403, permission_denied_message
from voto_studio_backend.spatial.models import DataSet


FIELD_TYPE_MAPPINGS = {
    'AutoField': 'number',
    'IntegerField': 'number',
    'PositiveIntegerField': 'number',
    'FloatField': 'number',
    'CharField': 'text',
    'TextField': 'textarea',
    'BooleanField': 'checkbox',
    'DateField': 'date',
    'DateTimeField': 'datetime-local',
    'ChoiceField': 'select',
    'JSONField': 'json',
    'OneToOneField': 'select',
    'ForeignKey': 'select',
    'ManyToManyField': 'select',
}


MEDIA_MODEL_KEYS = (
    'images',
    'videos',
    'resources',
)


MEDIA_MODEL_MAPPINGS = {
    'media.Image': Image,
    'media': Video,
    'resources': Resource,
}


MEDIA_SERIALIZER_MAPPINGS = {
    'media.Image': ImageSerializer,
    'media.Video': VideoSerializer,
    'media.Resource': ResourceSerializer,
}


MEDIA_FIELD_SERIALIZER_MAPPINGS = {
    'images': ImageSerializer,
    'videos': VideoSerializer,
    'resources': ResourceSerializer,
}


MODEL_FIELD_MAP = {
    'media.Image': 'images',
    'media.Video': 'videos',
    'media.Resource': 'resources',
}


WORKSHOP_MODELS = settings.WORKSHOP_MODELS
MEDIA_MODELS = list(apps.get_app_config('media').get_models())


def is_forward_rel(field):
    return not (isinstance(field, OneToOneRel) or
                isinstance(field, ManyToOneRel) or
                isinstance(field, ManyToManyRel))


def get_name(field):
    """
    Depending on what side of a relationship an instance is, the field name will change.
    We can either get the ``name`` attribute or the ``related_name`` attribute.
    """
    if is_forward_rel(field):
        return field.name
    else:
        return field.related_name


def get_field(field_name, model=None, instance=None):
    if model and instance:
        raise ValueError("You can't set bot the 'instance' and the 'model' arguments.")

    model_class = model if model else instance._meta.model
    field = model_class._meta.get_field(field_name)

    return field


def get_fields(model=None, instance=None):
    if model and instance:
        raise ValueError("You can't set bot the 'instance' and the 'model' arguments.")

    model_class = model if model else instance._meta.model
    fields = [
        f for f in model_class._meta.get_fields()
        if f.name not in model_class.hidden_fields
    ]

    return fields


def get_field_value(instance, field=None, field_name=None):
    """
    Depending on what side of a relationship an instance is, accessing the related instance(s)
    is different. One side is accessed using the name of field and the other is accessed using
    ``NAME_OF_FIELD_set``.
    """
    if field_name is not None:
        field = get_field(field_name, instance=instance)

    if is_forward_rel(field):
        return getattr(instance, field.name)
    else:
        return getattr(instance, f'{field.name}')


def get_field_type(field):
    """
    We need to convert Django's field type to the standard HTML form field types.
    """
    field_type = field.get_internal_type()

    if field_type == 'CharField':
        return FIELD_TYPE_MAPPINGS[field_type if not field.choices else 'ChoiceField']

    return FIELD_TYPE_MAPPINGS[field_type]


def get_related_instances(instance, field, using=settings.STUDIO_DB):
    """
    For a given instance get the related manager for the field's related model class and use
    it to get all the instances of the model whose ``tracked`` attribute is ``True``.
    """
    if instance:
        model_class = field.related_model
        instances = model_class.objects \
            .using(using) \
            .filter(tracked=True, id__in=[o.id for o in get_field_value(instance, field=field).all()])

        return {
            'instances': serializers.GeneralSerializer(instances, model_class=model_class, many=True).data,
            'table_heads': model_class.get_table_heads(model_class, verbose=True),
        }

    return {
        'instances': [],
        'table_heads': [],
    }


def get_options(instance, field, using=settings.STUDIO_DB):
    """
    Both OneToOne and ForeignKey (OneToMany) fields require a dropdown menu to select a value as the
    "One" part of both relationships terminates with the instance being edited. So we need to look at
    the field provided and return all the possible options for the select field.
    """
    field_type = field.get_internal_type()
    model_class = field.model
    related_model_class = field.related_model

    if field.choices:
        ret = {'options': [{'label': b, 'value': a} for a, b in field.choices]}
        ret['options'].insert(0, {'label': 'None', 'value': ''})

        return ret

    if field_type == 'ForeignKey':
        if instance:
            blacklist_ids = [getattr(get_field_value(instance, field=field), 'id', None)]
            if isinstance(instance, related_model_class):
                blacklist_ids.append(instance.id)
            blacklist_ids = list(filter(lambda el: bool(el), blacklist_ids))

            instances = related_model_class.objects \
                .using(using) \
                .filter(tracked=True) \
                .exclude(id__in=blacklist_ids)

        else:
            instances = related_model_class.objects \
                .using(using) \
                .filter(tracked=True) \

        ret = {'options': []}
        for instance in instances:
            label = f"ID: {instance.id} "
            for descriptor in instance.get_table_values()['descriptors']:
                label += f"{descriptor['name'].replace('_', ' ').capitalize()}: {descriptor['value'].capitalize()} | "
            ret['options'].append({
                'label': label, 'value': str(instance.id)
            })
        ret['options'].insert(0, {'label': 'None', 'value': ''})

        return ret

    if field_type == 'OneToOneField':
        if instance:
            blacklist_ids = [getattr(get_field_value(instance, field=field), 'id', None)]
            if isinstance(instance, related_model_class):
                blacklist_ids.append(instance.id)
            blacklist_ids = list(filter(lambda el: bool(el), blacklist_ids))
            instances = [i for i in related_model_class.objects.filter(tracked=True).exclude(id__in=blacklist_ids)
                         if not hasattr(i, field.remote_field.name)]
        else:
            instances = [i for i in related_model_class.objects.filter(tracked=True)
                         if not hasattr(i, field.remote_field.name)]

        ret = {'options': []}
        for instance in instances:
            if not hasattr(instance, model_class._meta.model_name.lower()):
                label = f"ID: {instance.id} "
                for descriptor in instance.get_table_values()['descriptors']:
                    label += f"{descriptor['name'].capitalize()}: {descriptor['value'].capitalize()} "
                ret['options'].append({
                    'label': label, 'value': str(instance.id)
                })
        ret['options'].insert(0, {'label': 'None', 'value': ''})

        return ret

    return {}


def is_read_only(field):
    """
    Determine whether the field is read-only using the defined
    ``read_only_fields`` attribute of the model class.
    """

    return field.name in getattr(field.model, 'read_only_fields', ())


def parse_value(field, value):
    """
    The HTML input will always return a string, even if the type of the field is "number".
    So this method looks at the field type and converts the given value to the correct type.
    """
    field_type = field.get_internal_type()

    if field_type == 'FloatField':
        return float(value)
    if field_type == 'IntegerField':
        return int(value)

    return value


def get_basic_fields(model=None, instance=None):
    hidden_fields = model.hidden_fields if model else instance._meta.model.hidden_fields
    basic_fields = [
        f for f in get_fields(model=model, instance=instance)
        if not (
            f.get_internal_type() == 'ManyToManyField' or
            type(f) is OneToOneRel or
            type(f) is ManyToOneRel or
            f.name in hidden_fields
        )
    ]

    return basic_fields


def get_media_fields(model=None, instance=None):
    media_fields = [
        f for f in get_fields(model=model, instance=instance)
        if f.related_model in MEDIA_MODELS
    ]

    return media_fields


def get_related_fields(model=None, instance=None):
    model_class = model if instance is None else instance._meta.model
    related_fields = [
        f for f in model_class._meta.many_to_many
        if (f.related_model not in MEDIA_MODELS and
            f.name not in model.hidden_fields)
    ]

    return related_fields


def get_meta(model_class):
    meta = model_class._meta
    ret = {
        'model_label': meta.label,
        'app_label': meta.app_label,
        'model_name': meta.model_name,
        'verbose_name': meta.verbose_name,
        'verbose_name_plural': meta.verbose_name_plural,
        'verbose_name_plural_title': meta.verbose_name_plural.title(),
    }

    return ret


class BuildFormAPI(APIView):
    """
    Class providing API endpoints for the creation of the workshop forms.
    """
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def get(request):
        """
        Return the data needed to build the form for a given model.
        The app label and model name are provided in the query string.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        app_label = request.GET.get('al')
        model_name = request.GET.get('mn')
        model_class = get_model(app_label=app_label, model_name=model_name)
        using = settings.STUDIO_DB if not request.GET.get('using') else request.GET.get('using')
        new = request.GET.get('id') == 'new'

        instance = None
        if not new:
            instance = get_object_or_403(model_class, (request.user, 'read'), id=request.GET.get('id'))

        basic_fields = get_basic_fields(model=model_class)
        basic_fields_list = [{
            'name': underscore_to_camel(field.name),
            'verbose_name': field.name.replace('_', ' '),
            'type': get_field_type(field),
            'select': get_field_type(field) == 'select',
            'default_checked': field.get_internal_type() == 'BooleanField' and getattr(instance, field.name, False),
            'read_only': is_read_only(field),
            **get_options(instance, field, using=using),
        } for field in basic_fields]

        related_fields = get_related_fields(model=model_class)
        related_fields_list = [{
            'name': field.name,
            'type': FIELD_TYPE_MAPPINGS[field.get_internal_type()],
            'field_name': field.name,
            'related_instances': get_related_instances(instance, field, using=using),
            'option': {
                'label': field.name.replace('_', ' ').title(),
                'value': field.related_model._meta.label
            },
            'rels_dict': instance.rels_dict[field.name] if instance else get_rels_dict_default(field=field),
            **get_meta(field.related_model),
        } for field in related_fields]

        default_values = {}
        media_fields_dict = {key: [] for key in MEDIA_MODEL_KEYS}
        if instance:
            for field in basic_fields:
                field_value = getattr(instance, field.name)
                if not (field.get_internal_type() == 'ForeignKey' or field.get_internal_type() == 'OneToOneField'):
                    if not field.choices:
                        default_values[field.name] = field_value
                    else:
                        default_values[field.name] = {
                            'label': getattr(instance, f'get_{field.name}_display')(),
                            'value': field_value,
                        }
                else:
                    if field_value:
                        default_values[field.name] = {
                            'label': str(field_value),
                            'value': field_value.id,
                        }
                    else:
                        default_values[field.name] = {
                            'label': 'None',
                            'value': '',
                        }

            if instance.location_id_name:
                default_values[instance.location_id_name] = instance.location_id

            media_fields = get_media_fields(model=model_class)
            for field in media_fields:
                media_instances = [get_object_or_404(field.related_model, id=_id)
                                   for _id in instance.get_order(field.name)]
                media_fields_dict[field.name] = MEDIA_FIELD_SERIALIZER_MAPPINGS[field.name](
                    media_instances,
                    many=True
                ).data

        else:
            for field in basic_fields:
                if field.get_internal_type() == 'JSONField':
                    default_values[field.name] = field.get_default()

        response = {
            'new': new,
            'parent_model': {
                'id': request.GET.get('id') if not new else None,
                **get_meta(model_class),
            },
            'basic_fields': basic_fields_list,
            'media_fields': media_fields_dict,
            'related_fields': related_fields_list,
            'default_values': default_values,
            'location_id_name': instance.location_id_name if instance else 'Select Data Set',
        }

        return Response(response, status=status.HTTP_200_OK)


class UpdateBasicFieldsAPI(APIView):
    """
    Class providing API endpoints used to update the basic fields of an instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def post(request):
        """
        Handle the updating of all basic fields of an existing instance.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data['model_label']
        instance_id = request.data['id']
        model_class = get_model(model_label=model_label)

        new = instance_id == 'new'
        if new:
            instance = model_class.objects.create(user=request.user)
        else:
            instance = get_object_or_403(model_class, (request.user, 'write'), id=instance_id)

        basic_fields = get_basic_fields(model=model_class)
        values = request.data['values']
        if isinstance(values, str):
            values = json.loads(values)

        for field in basic_fields:
            if values.get(field.name):
                if not (field.get_internal_type() == 'ForeignKey' or field.get_internal_type() == 'OneToOneField'):
                    if not field.choices:
                        setattr(instance, field.name, parse_value(field, values[field.name]))
                    else:
                        setattr(instance, field.name, values[field.name]['value'])
                else:
                    related_instance_id = values[field.name]['value']
                    if related_instance_id:
                        related_instance = get_object_or_404(field.related_model, id=related_instance_id)
                        instance.add_fk(field, related_instance)
                        Change.objects.stage_updated(related_instance, request)
                    else:
                        related_instance = getattr(instance, field.name)
                        if related_instance:
                            instance.remove_fk(field, related_instance)
                            Change.objects.stage_updated(related_instance, request)

        try:
            instance.save(using=settings.STUDIO_DB)
            base_instance = Change.objects.stage_created_or_updated(instance, request, created=new)
        except IntegrityError as e:
            return Response({
                'result': {
                    'updated': False,
                    'error': str(e),
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        response = {
            'id': base_instance.id,
            'created': new,
            'updated': True,
            **get_meta(model_class),
        }

        return Response(response, status=status.HTTP_200_OK)


class UpdateMediaFieldAPI(APIView):
    authentication_classes = (authentication.TokenAuthentication, )

    @staticmethod
    def post(request):
        """
        Provide users with the capability to add images, videos and
        resources to pieces of content in VotoStudio.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data.get('model_label')
        instance_id = request.data.get('id')
        media_model_label = request.data.get('media_model_label')
        media_ids = request.data.get('media_ids')
        update_type = request.data.get('update_type')

        model_class = get_model(model_label=model_label)
        instance = get_object_or_403(model_class, (request.user, 'write'), id=instance_id)

        media_instances = get_model(model_label=media_model_label).objects.filter(id__in=media_ids)
        field_value = get_field_value(instance, field_name=MODEL_FIELD_MAP[media_model_label])

        if update_type == 'add':
            for media_instance in media_instances:
                field_value.add(media_instance)
                instance.extend_order(media_instance.id, MODEL_FIELD_MAP[media_model_label])

        if update_type == 'remove':
            for media_instance in media_instances:
                field_value.remove(media_instance)
                instance.reduce_order(media_instance.id, MODEL_FIELD_MAP[media_model_label])

        base_instance = Change.objects.stage_updated(instance, request)

        response = {
            'id': base_instance.id,
            'media_ids': media_ids,
            'media_model_label': media_model_label,
            'media_type': MODEL_FIELD_MAP[media_model_label],
            'update_type': update_type,
            'new_instances': MEDIA_SERIALIZER_MAPPINGS[media_model_label](media_instances, many=True).data,
        }

        return Response(response, status=status.HTTP_200_OK)


class UpdateMediaOrderAPI(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def post(request):
        """
        The first media instance in its respective order list in
        a piece of content's media order dict is "primary". This
        endpoint handles the persistence of media orders.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data.get('model_label')
        instance_id = request.data.get('id')
        result = request.data.get('result')
        media_type = request.data.get('media_type')

        model_class = get_model(model_label=model_label)
        instance = get_object_or_403(model_class, (request.user, 'write'), id=instance_id)

        if not instance.can_write(request.user):
            return Response({
                'message': 'User does not have permission to edit this piece of content.',
                'permitted': False,
            }, status=status.HTTP_401_UNAUTHORIZED)

        instance.update_order(result, media_type)
        base_instance = Change.objects.stage_updated(instance, request)

        response = {
            'id': base_instance.id,
            'media_type': media_type,
            'result': result,
            'order': base_instance.get_order(media_type),
        }

        return Response(response, status=status.HTTP_200_OK)


class UpdateRelatedFieldAPI(APIView):
    """
    Class providing API endpoints used to update the related fields of an instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def post(request):
        """
        Handle the updating of all related fields of an existing instance.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data['model_label']
        model_class = get_model(model_label=model_label)
        instance = get_object_or_403(model_class, (request.user, 'write'), id=request.data['id'])

        related_app_label, related_model_name = request.data['related_model_label'].split('.')
        related_model_class = get_model(app_label=related_app_label, model_name=related_model_name)
        related_instances = related_model_class.objects.filter(id__in=request.data.get('related_ids'))

        update_type = request.data['update_type']
        rel_level = None
        field_name = camel_to_underscore(request.data['field_name'])
        for related_instance in related_instances:
            field = get_field(field_name, instance=instance)
            if update_type == 'add':
                rel_level = request.data['rel_level']
                if rel_level == 'rel':
                    if related_instance.can_write(request.user):
                        instance.add_rel(field, related_instance)
                    else:
                        raise PermissionDenied(permission_denied_message({
                            'message': 'You do not have write permission on this content.',
                        }, instance=instance))
                elif rel_level == 'ref':
                        instance.add_ref(field, related_instance)
            elif update_type == 'remove':
                get_field_value(instance, field_name=field_name).remove(related_instance)
                instance.remove_rel(field, related_instance)

        instances = related_model_class.objects.filter(id__in=request.data.get('related_ids'))
        response = {
            'id': instance.id,
            'type': update_type,
            'rel_level': rel_level,
            'field_name': field_name,
            'field': {
                'model_label': model_class._meta.label,
                'model_name_verbose': model_class._meta.verbose_name,
            },
            'related_field': {
                'model_label': related_model_class._meta.label,
                'model_name_verbose': related_model_class._meta.verbose_name,
                'instances': serializers.GeneralSerializer(instances, model_class=related_model_class, many=True).data,
                'related_ids': request.data.get('related_ids'),
            },
        }

        Change.objects.bulk_stage_updated([instance, *related_instances], request)

        return Response(response, status=status.HTTP_200_OK)


class InstanceDetailAPI(APIView):
    """
    Class providing API endpoints relating to instance details.
    """
    @staticmethod
    def get(request):
        """
        Get the details for a given instance.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        app_label = request.GET.get('al')
        model_name = request.GET.get('mn')
        instance_id = request.GET.get('id')

        model_class = get_model(app_label=app_label, model_name=model_name)
        instance = get_object_or_403(model_class, (request.user, 'read'), id=instance_id)

        response = {
            'item': serializers.GeneralDetailSerializer(instance, model_class=model_class).data,
        }

        return Response(response, status=status.HTTP_200_OK,)


class PublishError(Exception):
    pass


class PublishInstancesAPI(APIView):
    """
    Class providing API endpoints used to publish changes.
   """
    @staticmethod
    def post(request):
        """
        Given an instance, publish it.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data['model_label']
        instance_ids = request.data['instance_ids']

        model_class = get_model(model_label=model_label)
        instance = get_object_or_403(model_class, (request.user, 'commit'), id=instance_ids[0])

        committed_changes = Change.objects.commit_for_instance(instance)

        if not len(committed_changes):
            raise PublishError({
                'message': 'No changes have been made since the last publish.'
            })

        response = {
            'changes_committed': [c.id for c in committed_changes],
        }

        return Response(response, status=status.HTTP_200_OK)


class DeleteInstancesAPI(APIView):
    """
    Class providing API endpoints used to delete instances.
    """
    @staticmethod
    def delete(request):
        """
        Delete a given instance.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data['model_label']
        instance_ids = request.data['ids']
        model_class = get_model(model_label=model_label)

        for instance_id in instance_ids:
            instance = get_object_or_403(model_class, (request.user, 'write'), id=instance_id)
            instance.delete(fake=False)
            Change.objects.stage_deleted(instance, request)

            instance = get_object_or_403(
                model_class.objects.using(settings.MAIN_SITE_DB),
                (request.user, 'write'),
                id=instance_id,
            )
            instance.delete(fake=False)

        response = {
            'ids': instance_ids,
            'model_label': model_label,
        }

        return Response(response, status=status.HTTP_200_OK)


class InstanceListAPI(APIView):
    """
    Class providing API endpoints used to list instances.
    """
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.GET.get('ml')
        model_class = get_model(model_label=model_label)

        must_not = []

        instance_id = request.GET.get('id')
        field_name = request.GET.get('fn')
        if not instance_id == 'null' and instance_id is not None:
            model_class = get_model(model_label=model_label)
            instance = get_object_or_404(model_class, id=instance_id)
            related_instances = get_field_value(instance, field_name=field_name).all()
            must_not = [instance.id for instance in related_instances]

        instances = model_class.objects \
            .filter(tracked=True) \
            .exclude(id__in=must_not) \
            .order_by('-id')

        search = request.GET.get('search', None)
        if search not in (None, ''):
            instances = instances \
                .annotate(search=SearchVector(*model_class.search_fields)) \
                .filter(search=search)

        page = request.GET.get('page', 0)
        size = request.GET.get('size', 10)
        from_, to = create_slice(page, size)
        instances = instances[from_:to]

        response = {
            'count': model_class.objects.filter(tracked=True).count(),
            'list': {
                'instances': serializers.GeneralSerializer(instances, model_class=model_class, many=True).data,
                'table_heads': model_class.get_table_heads(model_class, verbose=True),
                'model_label': model_label,
                'model_name': model_class._meta.model_name,
                'verbose_name': model_class._meta.verbose_name,
            }
        }

        return Response(response, status=status.HTTP_200_OK)


class RelatedInstanceListAPI(APIView):
    """
    Class providing API endpoints used to list instances.
    """
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        related_model_label = request.GET.get('rml')
        related_model_class = get_model(model_label=related_model_label)

        must_not = []

        instance_id = request.GET.get('id')
        model_label = request.GET.get('ml')
        field_name = request.GET.get('fn')
        if not instance_id == 'null' and instance_id is not None:
            model_class = get_model(model_label=model_label)
            instance = get_object_or_404(model_class, id=instance_id)
            related_instances = get_field_value(instance, field_name=field_name).all()
            must_not = [instance.id for instance in related_instances]

        instances = related_model_class.objects \
            .filter(tracked=True) \
            .exclude(id__in=must_not) \
            .order_by('-id')

        search = request.GET.get('search', None)
        if search not in (None, ''):
            instances = instances \
                .annotate(search=SearchVector(*related_model_class.search_fields)) \
                .filter(search=search)

        page = request.GET.get('page', 0)
        size = request.GET.get('size', 10)
        from_, to = create_slice(page, size)
        instances = instances[from_:to]

        response = {
            'count': related_model_class.objects.filter(tracked=True).count(),
            'list': {
                'instances': serializers.GeneralSerializer(instances, model_class=related_model_class, many=True).data,
                'table_heads': related_model_class.get_table_heads(related_model_class, verbose=True),
                'model_label': related_model_label,
                'model_name': related_model_class._meta.model_name,
                'verbose_name': related_model_class._meta.verbose_name,
            }
        }

        return Response(response, status=status.HTTP_200_OK)


class InstanceFinderAPI(APIView):
    """
    Class providing API endpoints used to build the instance finder.
    """
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        ret = []
        options = []
        for model_label in WORKSHOP_MODELS:
            model_class = get_model(model_label=model_label)
            ret.append({
                'model_label': model_label,
                'app_label': model_class._meta.app_label,
                'model_name': model_class._meta.model_name,
                'verbose_name': model_class._meta.verbose_name,
                'verbose_name_plural': model_class._meta.verbose_name_plural,
                'verbose_name_plural_title': model_class._meta.verbose_name_plural.title(),
            })
            options.append({
                'label': model_class._meta.verbose_name.title(),
                'value': model_label,
            })

        response = {
            'finder': {
                'items': ret,
                'options': options,
            },
        }

        return Response(response, status=status.HTTP_200_OK)


class LocationPickerAPI(APIView):
    """
    Class providing API endpoints used to provide the data set
    for the location picker in VotoStudio's forms.
    """
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        data_set = get_object_or_404(DataSet.objects.using(settings.SPATIAL_DB), location_id_name='CIRCUITO')

        response = {
            'data_set': {
                'name': data_set.name,
                'geojson': data_set.to_dict(),
            },
            # The ``location_id_name`` is specific to each data set
            'location_id_name': data_set.location_id_name,
        }

        return Response(response, status=status.HTTP_200_OK)
