import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, OneToOneRel
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shared.utils import hidden_fields
from voto_studio_backend.forms.models import InfoMixin, JSONModel, JSONAutoField, JSONCharField
from voto_studio_backend.permissions.models import PermissionsBaseModel
from voto_studio_backend.search.models import IndexingManager, IndexingMixin


STUDIO_DB = settings.STUDIO_DB
MAIN_SITE_DB = settings.MAIN_SITE_DB
HISTORY_DB = settings.HISTORY_DB


STAGE_CREATED = 'created'
STAGE_UPDATED = 'updated'
STAGE_DELETED = 'deleted'


STAGE_OPTIONS = (
    (STAGE_CREATED, STAGE_CREATED),
    (STAGE_UPDATED, STAGE_UPDATED),
    (STAGE_DELETED, STAGE_DELETED),
)


def _get_content_type(instance=None, model=None):
    """
    Helper method to return the contents type of model provided or the contents
    type of the model of which the provided instance is an instance of.
    """
    if instance is not None and model is not None:
        raise ValueError("Provide only an 'instance' or a 'model'.")
    if instance is not None:
        return ContentType.objects.get_for_model(instance._meta.model)
    if model is not None:
        return ContentType.objects.get_for_model(model)


class ChangeManager(models.Manager):
    """Custom model manager for Change"""
    def _get_one_to_one_fields(self, instance):
        one_to_one_fields = [f for f in instance._meta.get_fields() if
                             f.get_internal_type() == 'OneToOneField' and not isinstance(f, OneToOneRel)]

        return one_to_one_fields

    def _copy_instance(self, instance):
        """
        By clearing the ID of an instance and then saving, Django will perform an INSERT
        action, thus creating a new instance with the same data but a new, unique ID.
        """
        base_instance_id = instance.id
        instance.id = None
        instance.tracked = False
        for field in instance._meta.get_fields():
            if not field.is_relation and field.unique and not field.name == 'id':
                setattr(instance, field.name, f'{getattr(instance, field.name)}-{uuid.uuid4()}')
        for field in self._get_one_to_one_fields(instance):
            setattr(instance, f'{field.name}_id', None)
        instance.save(using=STUDIO_DB)
        base_instance = get_object_or_404(instance._meta.model, id=base_instance_id)

        return base_instance, instance

    def _create_change(self, stage_type, instance, request=None, parent=None):
        """
        Create the change instance for a 'created', 'updated' or 'deleted' instance
        and store representations of any OneToOne or ManyToMany relationships as dictionaries.
        """
        content_type = _get_content_type(instance=instance)
        parent_content_type = _get_content_type(instance=parent)
        parent_object_id = parent.id if parent else None
        base_instance, copy_instance = self._copy_instance(instance)
        description = f'{str(request.user)} {stage_type} {base_instance._meta.model_name} {str(base_instance)}'

        change = self.using(STUDIO_DB).model(
            stage_type=stage_type,
            description=description,
            content_type=content_type,
            object_id=copy_instance.id,
            base_id=base_instance.id,
            parent_content_type=parent_content_type,
            parent_object_id=parent_object_id,
            user=request.user,
        )
        change.one_to_one_models = {f.name: getattr(base_instance, f.name).id for f
                                    in self._get_one_to_one_fields(instance)
                                    if getattr(base_instance, f.name, False)}
        change.many_to_many_models = {f.name: [o.id for o in getattr(base_instance, f.name).all()]
                                      for f in instance._meta.many_to_many}
        change.save(using=STUDIO_DB)

        return change, base_instance

    def stage_created(self, instance, request, parent=None):
        """
        Create a copy of the instance being created and generate a change instance for
        the creation of an instance made using the rest API.
        """
        _, base_instance = self._create_change(STAGE_CREATED, instance, request=request, parent=parent)

        return base_instance

    def stage_updated(self, instance, request, parent=None):
        """
        Create a copy of the instance being changed and generate a change instance for
        a change made using the rest API.
        """
        _, base_instance = self._create_change(STAGE_UPDATED, instance, request=request, parent=parent)

        return base_instance

    def stage_deleted(self, instance, request, parent=None):
        """
        Create a copy of the instance being deleted and generate change instance for
        the deletion made using the rest API.
        """
        _, base_instance = self._create_change(STAGE_DELETED, instance, request=request, parent=parent)

        return base_instance

    def stage_created_or_updated(self, instance, request, parent=None, created=True):
        if created:
            return self.stage_created(instance, request, parent)
        else:
            return self.stage_updated(instance, request, parent)

    def bulk_stage_created(self, instances, request, parent=None):
        """
        Stage create changes for each instance in the list of instances provided.
        """
        if not isinstance(instances, list):
            raise ValueError('Provide a list of instances.')
        base_instances = [self.stage_created(instance, request, parent=parent) for instance in instances]

        return base_instances

    def bulk_stage_updated(self, instances, request, parent=None):
        if not isinstance(instances, list):
            raise ValueError('Provide a list of instances.')
        base_instances = [self.stage_updated(instance, request, parent=parent) for instance in instances]

        return base_instances

    def bulk_stage_deleted(self, instances, request, parent=None):
        if not isinstance(instances, list):
            raise ValueError('Provide a list of instances.')
        base_instances = [self.stage_deleted(instance, request, parent=parent) for instance in instances]

        return base_instances

    def get_for_model(self, model, request=None, committed=False, using=STUDIO_DB):
        """
        Get a collection of either all committed or all non-committed
        changes for a particular model, ordered by date with earliest first.
        """
        content_type = _get_content_type(model=model)
        user = getattr(request, 'user', None)
        changes = Change.objects \
            .using(using) \
            .filter(content_type=content_type, user=user, committed=committed)

        return changes

    def get_for_instance(self, instance, committed=False, using=STUDIO_DB):
        """
        Get a collection of either all committed or all non-committed
        changes for an instance, ordered by date with earliest first.
        """
        content_type = _get_content_type(instance=instance)
        changes = Change.objects \
            .using(using) \
            .filter(content_type=content_type, base_id=instance.id, committed=committed)

        return changes

    def commit_for_instance(self, instance, using=STUDIO_DB):
        changes = self.get_for_instance(instance, using=using)
        return [change.commit() for change in changes.order_by('date_created')]


class Change(models.Model):
    """Stores information relevant to a change event. Also stores the type of object changed."""
    stage_type = models.CharField(_('Stage type'), blank=True, max_length=128, choices=STAGE_OPTIONS)
    description = models.CharField(_('Change description'), blank=True, max_length=256)
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.CASCADE,
        related_name='change_content_type',
    )
    object_id = models.PositiveIntegerField(_('Copy instance id'), null=True)
    base_id = models.PositiveIntegerField(_('Base instance id'), null=True)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    parent_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='change_parent_content_type',
    )
    parent_object_id = models.PositiveIntegerField(_('Parent instance id'), null=True, blank=True)
    parent_content_object = GenericForeignKey(ct_field='parent_content_type', fk_field='parent_object_id')
    one_to_one_models = JSONField(
        _("Fully describes base instance's one to one rels"),
        blank=True,
        null=True,
        default=dict
    )
    many_to_many_models = JSONField(
        _("Describes base instance's many to manys rels"),
        blank=True,
        null=True,
        default=dict
    )
    date_created = models.DateTimeField(_('Date of creation'), default=timezone.now)
    committed = models.BooleanField(_('Whether the change has been committed'), default=False)
    date_committed = models.DateTimeField(_('Date of commit'), default=timezone.now)
    reverted = models.BooleanField(_('Whether the change has been reverted'), default=False)
    date_reverted = models.DateTimeField(_('Date of revert'), default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    objects = ChangeManager()

    def __str__(self):
        return f'{self.id} | {self.description}'

    def _get_instance(self, using=STUDIO_DB, base=True):
        """
        Get the instance that the change instance is related to.
        Could this implementation be made simpler with self.content_object?
        """
        instance_id = self.base_id if base else self.object_id

        return get_object_or_404(self.content_type.model_class().objects.using(using), id=instance_id)

    @staticmethod
    def _parse_json_fields(instance):
        fields = instance._meta.model._meta.get_fields()
        for field in fields:
            if field.name in ('statistics', 'experience', 'references'):
                sub_instances = getattr(instance, field.name)['sub_instances']
                parsed_field = []
                if len(sub_instances):
                    for sub_instance in sub_instances:
                        parsed_field.append({
                          field['name']: field['value'] for field in sub_instance['fields']
                        })
                    setattr(instance, field.name, parsed_field)
                else:
                    setattr(instance, field.name, [])

        return instance

    def commit(self, to_index=True, commit_base=False):
        """
        Commit a change instance and propagate changes through to the main_site database. Will
        create a new instance or update/delete an existing one.
        """
        if self.stage_type == STAGE_CREATED or self.stage_type == STAGE_UPDATED:
            # Update some properties on the base instance. This is so
            # we can display whether or not an instance is visible on
            # the main in VotoStudio.
            base_instance = self._get_instance(using=STUDIO_DB, base=True)
            if not base_instance.published:
                base_instance.published = True
            base_instance.date_last_published = timezone.now()
            base_instance.save(using=STUDIO_DB)

            # Get the instance that we are going to copy over to the
            # main site database. We need to parse the JSON fields
            # into a format that is more friendly to the main site.
            instance = self._get_instance(using=STUDIO_DB, base=commit_base)
            instance = self._parse_json_fields(instance)
            instance.id = self.base_id
            instance.tracked = True

            # Remove all ForeignKeys apart from User
            fk_fields = [field for field in instance._meta.get_fields()
                         if (field.get_internal_type() == 'ForeignKey' and not
                             field.related_model._meta.label == settings.AUTH_USER_MODEL)]
            for fk_field in fk_fields:
                setattr(instance, f'{fk_field.name}_id', None)
            instance.save(using=MAIN_SITE_DB, to_index=to_index)

        if self.stage_type == STAGE_DELETED:
            # Do nothing as this action can't
            # be "committed". By deleting an
            # instance it is deleted from all
            # databases and its ElasticSearch
            # index is deleted. Therefore there
            # is no further action to take.
            pass

        self.committed = True
        self.date_committed = timezone.now()
        self.save(using=STUDIO_DB)

        return self

    def revert(self):
        """"""
        raise NotImplementedError('The revert functionality is yet to be implemented.')


class TrackedModel(PermissionsBaseModel):
    """
    Adds several fields a model to integrate it with the changes app.
    If a model inherits from this then its changes will be tracked.
    """
    date_created = models.DateTimeField(_('Date of Creation'), default=timezone.now)
    tracked = models.BooleanField(_('Tracked'), default=True)
    published = models.BooleanField(_('Published'), default=False)
    date_last_published = models.DateTimeField(_('Date of Last Publish'), blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    search = IndexingManager()

    read_only_fields = ('date_created', 'user',)
    hidden_fields = hidden_fields()

    class Meta:
        abstract = True

    def delete(self, *args, fake=False, using=STUDIO_DB, **kwargs):
        """
        Implement some custom logic to alter the default
        behaviour of the ``instance.delete()`` method.
        """
        if fake:
            if using == STUDIO_DB:
                self.tracked = False
                self.save(using=STUDIO_DB)

                return self
            else:
                raise ValueError("The 'fake' keyword argument can only be set when using the STUDIO_DB.")
        else:
            super().delete(*args, using=using, **kwargs)


def get_order_default():
    return {
        'images': [],
        'videos': [],
        'resources': [],
    }


RELATIONSHIPS = 'rels'
REFERENCES = 'refs'


MEDIA_MODELS = (
    'media.Image',
    'media.Video',
    'media.Resource',
)


def _get_single_dict(field):
    field_type = field.get_internal_type()
    model_label = field.related_model._meta.label

    if field_type == 'OneToOneField':
        return {
            'id': None,
            'model_label': model_label,
            'type': field_type,
        }
    if field_type == 'ForeignKey':
        return {
            'ids': [],
            'model_label': model_label,
            'type': field_type,
        }
    if field_type == 'ManyToManyField':
        return {
            RELATIONSHIPS: [],
            REFERENCES: [],
            'model_label': model_label,
            'type': field_type,
        }


def get_rels_dict_default(field=None, fields=None):
    if field is not None:
        return _get_single_dict(field)
    if fields is not None:
        return {
            field.name: _get_single_dict(field) for field in fields
            if field.related_model._meta.label not in MEDIA_MODELS
        }


class TrackedWorkshopModelManager(models.Manager):
    def _get_fields(self):
        fields = [field for field in self.model._meta.get_fields() if field.is_relation]
        fields = [field for field in fields if field.name not in self.model.hidden_fields]
        fields = [field for field in fields if not field.related_model._meta.label.startswith('media')]

        return fields

    def create(self, **kwargs):
        instance = super().create(
            rels_dict=get_rels_dict_default(fields=self._get_fields()),
            **kwargs,
        )

        return instance

    def get_or_create(self, **kwargs):
        try:
            instance, new = self.get(**kwargs), False
        except self.model.DoesNotExist:
            instance, new = self.create(**kwargs), True

        return instance, new


class Statistics(JSONModel):
    id = JSONAutoField(unique=True)
    icon = JSONCharField(max_length=128)
    name = JSONCharField(max_length=128)
    value = JSONCharField(max_length=128)


class TrackedWorkshopModel(TrackedModel, InfoMixin, IndexingMixin):
    source = models.URLField(_('Source'), max_length=2048, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    statistics = JSONField(_('Statistics'), blank=True, null=True, default=Statistics())

    location_id_name = models.CharField(_('Location Identifier Name'), max_length=32, null=True, blank=True)
    location_id = models.CharField(_('Location Identifier'), max_length=32, null=True, blank=True)

    views = models.PositiveIntegerField(default=0)

    rels_dict = JSONField(_('Relationships Dictionary'), blank=True, default=dict)

    order = JSONField(_('Media Content Order'), blank=True, default=get_order_default)
    images = models.ManyToManyField('media.Image', blank=True)
    videos = models.ManyToManyField('media.Video', blank=True)
    resources = models.ManyToManyField('media.Resource', blank=True)

    objects = TrackedWorkshopModelManager()

    read_only_fields = ('date_created', 'user',)
    hidden_fields = hidden_fields(fields_tuple=('order', 'views', 'location_id_name', 'location_id',))

    class Meta:
        abstract = True

    def save(self, *args, to_index=True, **kwargs):
        self.to_index = to_index
        super().save(*args, **kwargs)

    def _get_field_value(self, field=None, field_name=None):
        _field_name = field_name
        if field is not None:
            _field_name = field.name
        return getattr(self, _field_name)

    @staticmethod
    def _flatten_rels_dict(rels_dict):
        ret = {}
        for key, inner_rel_dict in rels_dict.items():
            if inner_rel_dict['type'] == 'OneToOneField':
                flattened_inner_rel_dict = {key: inner_rel_dict}
            elif inner_rel_dict['type'] == 'ForeignKey':
                flattened_inner_rel_dict = {
                    key: {
                        **inner_rel_dict,
                        'ids': list(set(inner_rel_dict['ids']))
                    }
                }
            elif inner_rel_dict['type'] == 'ManyToManyField':
                flattened_inner_rel_dict = {
                    key: {
                        **inner_rel_dict,
                        RELATIONSHIPS: list(set(inner_rel_dict[RELATIONSHIPS])),
                        REFERENCES: list(set(inner_rel_dict[REFERENCES])),
                    },
                }
            else:
                flattened_inner_rel_dict = inner_rel_dict
            ret.update(flattened_inner_rel_dict)

        return ret

    def _add_to_rels_dict(self, field, instance, rel_level=None):
        field_type = field.get_internal_type()
        rels_dict = self.rels_dict

        if field_type == 'OneToOneField':
            rels_dict[field.name]['id'] = instance.id
            ins_rels_dict = instance.rels_dict
            ins_rels_dict[field.remote_field.name]['id'] = self.id

        elif field_type == 'ForeignKey':
            rels_dict[field.name]['ids'] = [instance.id]
            ins_rels_dict = instance.rels_dict
            ins_rels_dict[field.remote_field.name]['ids'].append(self.id)

        elif field_type == 'ManyToManyField':
            if rel_level == RELATIONSHIPS:
                ins_rels_dict = instance.rels_dict
                ins_rels_dict[self._meta.model.related_name][RELATIONSHIPS].append(self.id)
            rels_dict[field.name][rel_level].append(instance.id)

        instance.rels_dict = self._flatten_rels_dict(ins_rels_dict)
        instance.save(using=settings.STUDIO_DB)

        self.rels_dict = self._flatten_rels_dict(rels_dict)
        self.save(using=settings.STUDIO_DB)

    def _remove_from_rels_dict(self, field, instance):
        field_type = field.get_internal_type()
        rels_dict = self.rels_dict

        if field_type == 'OneToOneField':
            rels_dict[field.name]['id'] = None
        elif field_type == 'ForeignKey':
            rels_dict[field.name]['ids'].remove(instance.id)
            ins_rels_dict = instance.rels_dict
            ins_rels_dict[self._meta.model_name.lower()]['ids'].remove(self.id)
            instance.rels_dict = self._flatten_rels_dict(ins_rels_dict)
            instance.save(using=settings.STUDIO_DB)
        elif field_type == 'ManyToManyField':
            for rel_level in (RELATIONSHIPS, REFERENCES):
                try:
                    rels_dict[field.name][rel_level].remove(instance.id)
                except ValueError:
                    pass

        self.rels_dict = self._flatten_rels_dict(rels_dict)
        self.save(using=settings.STUDIO_DB)

    def set_order(self, order, media_type):
        order_dict = self.order
        order_dict[media_type] = order
        self.order = order_dict
        self.save()

    def get_order(self, media_type):
        order = self.order[media_type]
        return [int(id) for id in order if id]

    def extend_order(self, media_id, media_type):
        order = self.get_order(media_type)
        order.append(media_id)
        self.set_order(order, media_type)

    def reduce_order(self, media_id, media_type):
        order = self.get_order(media_type)
        order.remove(media_id)
        self.set_order(order, media_type)

    def update_order(self, result, media_type):
        order = self.get_order(media_type)
        source_index = result['source']['index']
        order = [*order[0:source_index], *order[source_index + 1:]]
        order.insert(result['destination']['index'], result['draggable_id'])
        self.set_order(order, media_type)

    def add_rel(self, field, instance):
        self._get_field_value(field=field).add(instance)
        self._add_to_rels_dict(field, instance, rel_level=RELATIONSHIPS)

    def remove_rel(self, field, instance):
        self._get_field_value(field=field).remove(instance)
        self._remove_from_rels_dict(field, instance)

    def add_ref(self, field, instance):
        self._get_field_value(field=field).add(instance)
        self._add_to_rels_dict(field, instance, rel_level=REFERENCES)

    def remove_ref(self, field, instance):
        self.remove_rel(field, instance)

    def add_fk(self, field, instance):
        setattr(self, f'{field.name}_id', instance.id)
        self._add_to_rels_dict(field, instance)

    def remove_fk(self, field, instance):
        setattr(self, f'{field.name}_id', None)
        self._remove_from_rels_dict(field, instance)


class ChangeGroupManager(models.Manager):
    """Custom model manager for the ChangeGroup model"""
    def publish(self, instance, request):
        """
        Commit all non-committed change instances for a particular
        instance and its child instances.
        """
        content_type = _get_content_type(instance=instance)
        query = Q(
            content_type=content_type, base_id=instance.id,
        ) or Q(
            parent_content_type=content_type, parent_object_id=instance.id,
        ) and Q(
            committed=False,
        )
        changes = Change.objects.filter(query).order_by('date_created')

        if not changes.count():
            return {'published': False, 'message': 'No changes made since last publish.'}
        changes_committed = [change.commit() for change in changes]

        description = f'{str(request.user)} published <{instance._meta.model_name}> instance {str(instance)}'
        change_group = self.model(
            description=description,
            date_created=timezone.now(),
            content_type=content_type,
            object_id=instance.id,
            user=request.user,
        )
        change_group.save(using=STUDIO_DB)
        change_group.changes_committed.set(changes_committed)

        return {'published': True, 'change_group': change_group}

    def bulk_commit(self, changes, request):
        """
        Commit all committed or non-committed changes in a list of
        change instances.
        """
        if not len(changes):
            return {'published': False, 'message': 'No changes made since last bulk commit.'}

        changes_committed = [change.commit() for change in changes]
        description = f'{str(request.user)} published {len(changes_committed)} workshop changes.'
        change_group = self.model(
            description=description,
            date_created=timezone.now(),
            user=request.user,
        )
        change_group.save(using=STUDIO_DB)
        change_group.changes_committed.set(changes_committed)

        return {'published': True, 'change_group': change_group}


class ChangeGroup(models.Model):
    """Holds information about a change group"""
    description = models.CharField(_('Short description of the change group'), max_length=128)
    date_created = models.DateTimeField(_('Date when change group committed'), blank=True)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_('ID of parent instance'), blank=True, null=True)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    changes_committed = models.ManyToManyField('Change', blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    objects = ChangeGroupManager()

    def __str__(self):
        return self.description
