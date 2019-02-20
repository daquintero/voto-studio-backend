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
from voto_studio_backend.search.models import IndexingManager, IndexingMixin
from voto_studio_backend.permissions.models import PermissionsBaseModel


STUDIO_DB = settings.STUDIO_DB
MAIN_SITE_DB = settings.MAIN_SITE_DB

STAGE_CREATED = 'created'
STAGE_UPDATED = 'updated'
STAGE_DELETED = 'deleted'


STAGE_OPTIONS = (
    ('created', 'created'),
    ('updated', 'updated'),
    ('deleted', 'deleted'),
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

    def get_for_model(self, model, request=None, committed=False):
        """
        Get a collection of either all committed or all non-committed
        changes for a particular model, ordered by date with earliest first.
        """
        content_type = _get_content_type(model=model)
        user = getattr(request, 'user', None)
        changes = Change.objects.filter(content_type=content_type, user=user, committed=committed)

        return changes

    def get_for_instance(self, instance, request=None, committed=False):
        """
        Get a collection of either all committed or all non-committed
        changes for an instance, ordered by date with earliest first.
        """
        content_type = _get_content_type(instance=instance)
        changes = Change.objects.filter(content_type=content_type, user=request.user, committed=committed)

        return changes


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

    def commit(self):
        """
        Commit a change instance and propagate changes through to the frontend database. Will
        create a new instance or update/delete an existing one. Will also take care of any
        ManyToMany relationships.
        """
        if self.stage_type == STAGE_DELETED:
            # TODO: Do we need to non-fake delete from the STUDIO_DB?
            instance = self._get_instance(using=STUDIO_DB)
            instance.delete(fake=False, using=STUDIO_DB)

            instance = self._get_instance(using=MAIN_SITE_DB)
            instance.delete(fake=False, using=MAIN_SITE_DB)

        if self.stage_type == STAGE_CREATED or self.stage_type == STAGE_UPDATED:
            instance = self._get_instance(using=STUDIO_DB, base=False)
            instance.id = self.base_id
            for field_name, rel_id in self.one_to_one_models.items():
                setattr(instance, f'{field_name[0]}_id', rel_id)

            instance.save(using=MAIN_SITE_DB)

            for field_name, rel_ids in self.many_to_many_models.items():
                field = getattr(instance, field_name)
                field.set(field.model.objects.using(MAIN_SITE_DB).filter(id__in=rel_ids))

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


def get_rels_dict_default(fields=None, single_dict_only=False):
    single_dict = {
        RELATIONSHIPS: [],
        REFERENCES: [],
    }

    if single_dict_only:
        return single_dict
    else:
        return {
            field.name: single_dict for field in fields
        }


class TrackedWorkshopModelManager(models.Manager):
    def _get_many_to_many(self):
        many_to_many_fields = [field for field in self.model._meta.get_fields()
                               if field.many_to_many]
        many_to_many_fields = [field for field in many_to_many_fields
                               if field.name not in self.model.hidden_fields]

        return many_to_many_fields

    def create(self, **kwargs):
        instance = super().create(**kwargs)
        instance.rels_dict = get_rels_dict_default(fields=self._get_many_to_many())
        instance.save(using=settings.STUDIO_DB)

        return instance

    def get_or_create(self, **kwargs):
        instance, new = super().get_or_create(**kwargs)
        if new:
            instance.rels_dict = get_rels_dict_default(fields=self._get_many_to_many())
            instance.save(using=settings.STUDIO_DB)

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

    rels_dict = JSONField(_('Relationships Dictionary'), blank=True, default=dict)

    order = JSONField(_('Media Content Order'), blank=True, default=get_order_default)
    images = models.ManyToManyField('media.Image', blank=True)
    videos = models.ManyToManyField('media.Video', blank=True)
    resources = models.ManyToManyField('media.Resource', blank=True)

    objects = TrackedWorkshopModelManager()

    read_only_fields = ('date_created', 'user',)
    hidden_fields = hidden_fields(fields_tuple=('order',))

    class Meta:
        abstract = True

    def _get_field_value(self, field=None, field_name=None):
        _field_name = field_name
        if field is not None:
            _field_name = field.name
        return getattr(self, _field_name)

    @staticmethod
    def _flatten_rels_dict(rels_dict):
        ret = {}
        for key, inner_rel_dict in rels_dict.items():
            flattened_inner_rel_dict = {
                key: {
                    RELATIONSHIPS: list(set(inner_rel_dict[RELATIONSHIPS])),
                    REFERENCES: list(set(inner_rel_dict[REFERENCES])),
                },
            }
            ret.update(flattened_inner_rel_dict)

        return ret

    def _add_to_rels_dict(self, field, instance, rel_level):
        rels_dict = self.rels_dict
        if rel_level == RELATIONSHIPS:
            ins_rels_dict = instance.rels_dict
            ins_rels_dict[self._meta.model.related_name][RELATIONSHIPS].append(self.id)
            instance.rels_dict = self._flatten_rels_dict(ins_rels_dict)
            instance.save(using=settings.STUDIO_DB)

        rels_dict[field.name][rel_level].append(instance.id)
        self.rels_dict = self._flatten_rels_dict(rels_dict)
        self.save(using=settings.STUDIO_DB)

    def _remove_from_rels_dict(self, field, instance):
        rels_dict = self.rels_dict
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
        self._add_to_rels_dict(field, instance, RELATIONSHIPS)

    def remove_rel(self, field, instance):
        self._get_field_value(field=field).remove(instance)
        self._remove_from_rels_dict(field, instance)

    def add_ref(self, field, instance):
        self._get_field_value(field=field).add(instance)
        self._add_to_rels_dict(field, instance, REFERENCES)

    def remove_ref(self, field, instance):
        self.remove_rel(field, instance)


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
