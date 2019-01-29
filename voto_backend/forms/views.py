import json

from django.conf import settings
from django.db import IntegrityError
from django.db.models.fields.related import OneToOneRel, ManyToOneRel
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from shared.api.parsers import camel_to_underscore, underscore_to_camel
from shared.utils import get_model
from . import serializers
from voto_backend.changes.models import Change, ChangeGroup
from voto_backend.changes.serializers import ChangeGroupSerializer


FIELD_TYPE_MAPPINGS = {
    'IntegerField': 'number',
    'FloatField': 'number',
    'CharField': 'text',
    'TextField': 'textarea',
    'BooleanField': 'checkbox',
    'DateTimeField': 'datetime-local',
    'ChoiceField': 'select',
    'OneToOneField': 'select',
    'ForeignKey': 'select',
    'ManyToManyField': 'select',
}


WORKSHOP_MODELS = settings.WORKSHOP_MODELS


class ModelListAPI(APIView):
    """
        Class providing API endpoints for listing
        the test_app that can be controlled.
        """
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def get(request):
        """
        Return a list of all the test_app that
        can be controlled in the workshop.
        """
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        response = []
        for model_label in WORKSHOP_MODELS:
            model_class = get_model(model_label=model_label)
            results = model_class.search.filter(must={'tracked': True, 'user': request.user.id})
            response.append({
                'model_label': model_label,
                'app_label': model_class._meta.app_label,
                'model_name': model_class._meta.model_name,
                'verbose_name': model_class._meta.verbose_name,
                'verbose_name_plural': model_class._meta.verbose_name_plural,
                'verbose_name_plural_title': model_class._meta.verbose_name_plural.title(),
                'count': len(results),
                'values': results,
                'table_heads': model_class.table_heads.fget(model_class) if results else [],
                'loaded': True,
            })

        return Response({'items': response}, status=status.HTTP_200_OK)


def is_forward_rel(field):
    field_type = field.get_internal_type()

    return (field_type == 'OneToOneField' or
            field_type == 'ForeignKey' or
            field_type == 'ManyToManyField')


def get_name(field):
    """
    Depending on what side of a relationship an instance is, the field name will change.
    We can either get the ``name`` attribute or the ``related_name`` attribute.
    """
    if is_forward_rel(field):
        return field.name
    else:
        return field.related_name


def get_field_value(instance, field):
    """
    Depending on what side of a relationship an instance is, accessing the related instance(s)
    is different. One side is accessed using the name of field and the other is accessed using
    ``NAME_OF_FIELD_set``.
    """
    if is_forward_rel(field):
        return getattr(instance, field.name)
    else:
        return getattr(instance, f'{field.name}_set')


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
        model_class = instance._meta.model
        instances = model_class.search.filter(
            must={'tracked': True, 'id': [o.id for o in get_field_value(instance, field).all()]},
            sort='-date_created',
            using=using,
        )

        return instances

    return []


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
            blacklist_ids = [getattr(get_field_value(instance, field), 'id', None)]
            if isinstance(instance, related_model_class):
                blacklist_ids.append(instance.id)
            blacklist_ids = list(filter(lambda el: bool(el), blacklist_ids))
            instances = related_model_class.search.filter(
                must={'tracked': True},
                must_not={'id': blacklist_ids},
                using=using,
                size=90,
            )
        else:
            instances = related_model_class.search.filter(
                must={'tracked': True},
                using=using,
                size=90,
            )

        ret = {'options': []}
        for instance in instances:
            label = f"ID: {instance.get('id')} "
            for descriptor in instance['table_values']['descriptors']['values']:
                label += f"{descriptor['name'].capitalize()}: {descriptor['value'].capitalize()} "
                ret['options'].append({
                    'label': label, 'value': str(instance.get('id'))
                })
        ret['options'].insert(0, {'label': 'None', 'value': ''})

        return ret

    if field_type == 'OneToOneField':
        if instance:
            blacklist_ids = [getattr(get_field_value(instance, field), 'id', None)]
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
                for descriptor in instance.table_values['descriptors']['values']:
                    label += f"{descriptor['name'].capitalize()}: {descriptor['value'].capitalize()} "
                ret['options'].append({
                    'label': label, 'value': str(instance.id)
                })
        ret['options'].insert(0, {'label': 'None', 'value': ''})

        return ret

    return {}


def get_or_create_instance(app_label, model_name, instance_id, request):
    """
    Get or create an instance of the model class defined by the ``app_label``
    and ``model_name`` parameters. Also return the model class used.
    """
    model_class = get_model(app_label=app_label, model_name=model_name)
    instance_id = instance_id if not (instance_id == 'new') else None

    return model_class, model_class.objects.get_or_create(id=instance_id, user=request.user)


def is_read_only(field):
    """
    Determine whether the field is read-only using the defined
    ``read_only_fields`` attribute of the model class.
    """
    # TODO: Look into doing this via the model fields themselves.
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


def get_fields(model=None, instance=None):
    if model and instance:
        raise ValueError("Invalid arguments. You can't set bot the 'instance' and the 'model' arguments.")

    model_class = model if model else instance._meta.model
    fields = [f for f in model_class._meta.get_fields() if not f.get_internal_type() == 'AutoField']

    return fields


def get_basic_fields(model=None, instance=None):
    basic_fields = [
        f for f in get_fields(model=model, instance=instance)
        if not (
            f.get_internal_type() == 'ManyToManyField' or
            type(f) is OneToOneRel or
            type(f) is ManyToOneRel or
            f.name in ('user', 'tracked', 'date_created')
            # f in TrackedModel._meta.get_fields()
        )
    ]

    return basic_fields


def get_related_fields(model=None, instance=None):
    related_fields = [
        f for f in get_fields(model=model, instance=instance)
        if f.get_internal_type() == 'ManyToManyField'
    ]

    # model_class = model if model else instance._meta.model
    # related_fields = model_class._meta.many_to_many

    return related_fields


class BuildFormAPI(APIView):
    """
    Class providing API endpoints for the creation of the workshop forms.
    """
    @staticmethod
    def get(request):
        """
        Return the data needed to build the form for a given model.
        The app label and model name are provided in the query string.
        """
        app_label = request.GET.get('al')
        model_name = request.GET.get('mn')
        model_class = get_model(app_label=app_label, model_name=model_name)
        using = settings.STUDIO_DB if not request.GET.get('using') else request.GET.get('using')
        new = request.GET.get('id') == 'new'

        instance = get_object_or_404(
            model_class,
            id=request.GET.get('id'),
        ) if not new else None

        basic_fields = get_basic_fields(model=model_class)
        basic_fields_list = [{
            'name': underscore_to_camel(f.name),
            'verbose_name': f.name.replace('_', ' '),
            'type': get_field_type(f),
            'select': get_field_type(f) == 'select',
            'default_checked': f.get_internal_type() == 'BooleanField' and getattr(instance, f.name, False),
            'read_only': is_read_only(f),
            **get_options(instance, f, using=using),
        } for f in basic_fields]

        related_fields = get_related_fields(model=model_class)
        related_fields_list = [{
            'name': get_name(f),
            'type': FIELD_TYPE_MAPPINGS[f.get_internal_type()],
            'model_label': f.related_model._meta.label,
            'verbose_name': f.related_model._meta.verbose_name,
            'verbose_name_plural': f.related_model._meta.verbose_name_plural,
            'field_name': f.name,
            'related_instances': get_related_instances(instance, f, using=using),
        } for f in related_fields]

        default_values = {}
        if instance:
            for field in basic_fields:
                field_value = getattr(instance, field.name)
                # TODO: could this if statement be: ``if not field.is_relation:``?
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
                            'value': field_value.id
                        }
                    else:
                        default_values[field.name] = {
                            'label': 'None',
                            'value': ''
                        }

        response = {
            'new': new,
            'parent_model': {
                'name': model_class._meta.verbose_name,
                'model_label': model_class._meta.label,
                'id': request.GET.get('id') if not new else None,
            },
            'basic_fields': basic_fields_list,
            'related_fields': related_fields_list,
            'default_values': default_values,
        }

        return Response({'form': response}, status=status.HTTP_200_OK)


class RelatedFieldsAPI(APIView):
    """
    Class providing API endpoints for actions relevant to related fields.
    """
    @staticmethod
    def get(request):
        """
        Given a parent and related model return the related instances.
        """
        using = settings.STUDIO_DB if not request.GET.get('using') else request.GET.get('using')

        parent_app_label = request.GET.get('pal')
        parent_model_name = request.GET.get('pmn')
        parent_model_class = get_model(app_label=parent_app_label, model_name=parent_model_name)
        parent_instance_id = request.GET.get('pid')
        parent_instance = None

        if not parent_instance_id == 'new':
            parent_instance = get_object_or_404(parent_model_class, id=parent_instance_id)

        related_app_label = request.GET.get('ral')
        related_model_name = request.GET.get('rmn')
        related_model_class = get_model(app_label=related_app_label, model_name=related_model_name)
        related_field_name = request.GET.get('rfn')
        related_field = related_model_class._meta.get_field(related_field_name)

        if parent_instance:
            blacklist_ids = [o.id for o in get_field_value(parent_instance, related_field).all()]
            blacklist_ids.insert(0, parent_instance_id)
        else:
            blacklist_ids = []

        instances = related_model_class.search.filter(
            must={'tracked': True},
            must_not={'id': blacklist_ids},
            using=using,
            size=90,
        )

        return Response(
            {
                'related_field_options': instances,
                'table_heads': related_model_class.table_heads.fget(related_model_class) if instances else [],
                'verbose_name': related_model_class._meta.verbose_name,
                'field_name': related_field_name,
            },
            status=status.HTTP_200_OK,
        )


class InstanceDetailAPI(APIView):
    """
    Class providing API endpoints relating to instance details.
    """
    @staticmethod
    def get(request):
        """
        Get the details for a given instance.
        """
        app_label = request.GET.get('al')
        model_name = request.GET.get('mn')
        instance_id = request.GET.get('id')

        model_class, (instance, new) = get_or_create_instance(app_label, model_name, instance_id, request)

        return Response(
            {'item': serializers.GeneralDetailSerializer(instance, model_class=model_class).data},
            status=status.HTTP_200_OK,
        )


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
        app_label, model_name = request.data['model_label'].split('.')
        model_class, (instance, new) = get_or_create_instance(app_label, model_name, request.data['id'], request)

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
                    try:
                        setattr(instance, f'{field.name}_id', values[field.name]['value'])
                        instance.save(using=settings.STUDIO_DB)

                    except IntegrityError as e:
                        return Response({
                            'result': {'updated': False, 'error': str(e)}
                        }, status=status.HTTP_400_BAD_REQUEST)

        instance.save(using=settings.STUDIO_DB)
        base_instance = Change.objects.stage_created_or_updated(instance, request, created=new)

        response = {
            'id': base_instance.id,
            'created': new,
            'updated': True,
            'model_name_verbose': model_class._meta.verbose_name,
        }

        return Response({'result': response}, status=status.HTTP_200_OK)


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
        app_label, model_name = request.data['model_label'].split('.')
        model_class, (instance, new) = get_or_create_instance(app_label, model_name, request.data['id'], request)

        # TODO: do we need to send the related model name, can we not just get it from the field itself?
        related_app_label, related_model_name = request.data['related_model_label'].split('.')
        related_model_class = get_model(app_label=related_app_label, model_name=related_model_name)
        related_instance = get_object_or_404(related_model_class, id=request.data['related_id'])

        update_type = request.data['update_type']
        field_name = camel_to_underscore(request.data['field_name'])
        field = model_class._meta.get_field(field_name)
        field_value = get_field_value(instance, field)

        if update_type == 'add':
            field_value.add(related_instance)
        elif update_type == 'remove':
            field_value.remove(related_instance)

        response = {
            'id': instance.id,
            'related_id': related_instance.id,
            'type': update_type,
            'field': {
                'model_label': model_class._meta.label,
                'model_name_verbose': model_class._meta.verbose_name,
                **serializers.GeneralListSerializer(instance, model_class=model_class).data,
            },
            'related_field': {
                'model_label': related_model_class._meta.label,
                'model_name_verbose': related_model_class._meta.verbose_name,
                **serializers.GeneralListSerializer(related_instance, model_class=model_class).data,
            },
        }

        if new:
            Change.objects.stage_created(instance, request)
        else:
            Change.objects.bulk_stage_updated([instance, related_instance], request)

        return Response({'result': response}, status=status.HTTP_200_OK)


class PublishInstanceAPI(APIView):
    """
    Class providing API endpoints used to publish changes.
   """
    @staticmethod
    def post(request):
        """
        Given an instance, publish it.
        """
        app_label = request.GET.get('al')
        model_name = request.GET.get('mn')
        instance_id = request.GET.get('id')

        model_class = get_model(app_label=app_label, model_name=model_name)
        instance = get_object_or_404(model_class, id=instance_id)

        committed_changes = Change.objects.commit_for_instance(instance, request)

        return Response({'changes_committed': [c.id for c in committed_changes]}, status=status.HTTP_200_OK)


class PublishContentAPI(APIView):
    """
    Class providing API endpoints used to publish changes.
    """
    @staticmethod
    def post(request):
        """
        Given a user publish all changes since the last publish event triggered.
        """
        changes = Change.objects.filter(user=request.user, committed=False).order_by('date_created')
        change_group = ChangeGroup.objects.bulk_commit(changes, request)

        if not change_group['published']:
            return Response({'error': change_group['message']}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ChangeGroupSerializer(change_group['change_group']).data, status=status.HTTP_200_OK)


class DeleteInstanceAPI(APIView):
    """
    Class providing API endpoints used to delete instances.
    """
    @staticmethod
    def delete(request):
        """
        Delete a given instance.
        """
        app_label = request.data.get('app_label')
        model_name = request.data.get('model_name')
        instance_id = request.data.get('id')
        model_class = get_model(app_label=app_label, model_name=model_name)

        instance = get_object_or_404(model_class, id=instance_id)
        instance = instance.delete(fake=True)
        instance = Change.objects.stage_deleted(instance, request)
        item = serializers.GeneralDetailSerializer(instance, model_class=model_class).data

        return Response({'item': item}, status=status.HTTP_200_OK)
