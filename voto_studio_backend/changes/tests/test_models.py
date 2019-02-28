import time

from django.db.models.fields.related import OneToOneRel
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.test import TestCase, RequestFactory, TransactionTestCase
from .. import models
from shared.testing.test_app.models import BasicModel, create_random_string
from shared.testing.es_test_cases import ESTestCase
from shared.testing.utils import create_test_user, create_instance
from voto_studio_backend.users.models import User

# TODO: are the ForeignKey relationships properly handled by the changes app?


class ChangeManagerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@bar.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.request = RequestFactory()
        self.request.user = self.user
        self.instance = create_instance(user=self.user)

    def test__get_content_type(self):
        with self.assertRaises(ValueError):
            models._get_content_type(
                instance=self.instance,
                model=self.instance._meta.model
            )

        content_type = models._get_content_type(instance=self.instance)
        self.assertIsInstance(content_type, ContentType)
        self.assertEqual(content_type.model_class(), BasicModel)

        content_type = models._get_content_type(model=self.instance._meta.model)
        self.assertIsInstance(content_type, ContentType)
        self.assertEqual(content_type.model_class(), BasicModel)

    def test__copy_instance(self):
        base_instance_id = self.instance.id
        base_instance, copy_instance = models.Change.objects._copy_instance(self.instance)

        self.assertFalse(copy_instance.tracked)
        fields = copy_instance._meta.get_fields()
        self.assertFalse(any([getattr(copy_instance, f.name) for f in fields
                              if f.get_internal_type() == 'OneToOneField' and not isinstance(f, OneToOneRel)]))

        self.assertFalse(any([getattr(copy_instance, f.name).values() for f in copy_instance._meta.many_to_many]))
        self.assertEqual(base_instance_id, base_instance.id)

        base_basic_fields = [f for f in base_instance._meta.get_fields() if not f.is_relation or f.name == 'id']
        new_basic_fields = [f for f in copy_instance._meta.get_fields() if not f.is_relation or f.name == 'id']
        self.assertEqual(base_basic_fields, new_basic_fields)

    def test__create_change(self):
        new_char_field = create_random_string()
        self.instance.char_field = new_char_field
        self.instance.save(using=settings.STUDIO_DB)
        parent = None
        change, base_instance = models.Change.objects._create_change(
            models.STAGE_UPDATED,
            self.instance,
            self.request,
            parent=parent
        )

        self.assertEqual(change.base_id, base_instance.id)
        self.assertNotEqual(change.object_id, base_instance.id)
        self.assertEqual(self.instance.char_field, new_char_field)
        self.assertEqual(base_instance.char_field, new_char_field)

        extra_instance = create_instance(user=self.user)
        self.instance.one_to_one_field = extra_instance
        self.instance.save(using=settings.STUDIO_DB)
        self.instance.many_to_many_field.add(extra_instance)
        parent = None
        change, base_instance = models.Change.objects._create_change(
            models.STAGE_UPDATED,
            self.instance,
            self.request,
            parent=parent
        )
        rel_change, rel_base_instance = models.Change.objects._create_change(
            models.STAGE_UPDATED,
            extra_instance,
            self.request,
            parent=parent
        )
        self.assertEqual(change.base_id, base_instance.id)
        self.assertEqual(rel_change.base_id, rel_base_instance.id)
        self.assertNotEqual(change.object_id, base_instance.id)
        self.assertNotEqual(rel_change.object_id, rel_base_instance.id)

        self.assertFalse(self.instance.many_to_many_field.all())
        self.assertFalse(extra_instance.many_to_many_field.all())

        self.assertEqual(change.one_to_one_models, {'one_to_one_field': rel_base_instance.id})
        self.assertEqual(change.many_to_many_models['many_to_many_field'], [rel_base_instance.id])
        self.assertEqual(rel_change.many_to_many_models['many_to_many_field'], [base_instance.id])

    def test_stage_created(self):
        new_instance = create_instance(user=self.user)
        new_instance_id = new_instance.id
        base_instance = models.Change.objects.stage_created(new_instance, self.request)

        self.assertEqual(new_instance_id, base_instance.id)

    def test_stage_updated(self):
        base_instance_id = self.instance.id
        new_char_field = create_random_string()
        self.instance.char_field = new_char_field
        self.instance.save(using=settings.STUDIO_DB)
        base_instance = models.Change.objects.stage_updated(self.instance, self.request)

        self.assertEqual(base_instance_id, base_instance.id)
        self.assertEqual(base_instance.char_field, new_char_field)

    def test_stage_deleted(self):
        instance_to_delete = create_instance(user=self.user)
        instance_to_delete.delete(fake=True)
        base_instance = models.Change.objects.stage_deleted(instance_to_delete, self.request)

        self.assertFalse(base_instance.tracked)
        self.assertIsNotNone(get_object_or_404(BasicModel, id=base_instance.id))

    def test_stage_created_or_updated(self):
        new_instance = create_instance(user=self.user)
        base_instance = models.Change.objects.stage_created_or_updated(new_instance, self.request, created=True)

        self.assertTrue(base_instance)

        new_char_field = create_random_string()
        base_instance.char_field = new_char_field
        base_instance.save(using=settings.STUDIO_DB)

        updated_base_instance = models.Change.objects.stage_created_or_updated(
            base_instance,
            self.request,
            created=False
        )

        self.assertEqual(updated_base_instance.char_field, new_char_field)

    def test_bulk_stage_created(self):
        ...

    def test_bulk_stage_updated(self):
        instances = [create_instance(user=self.user) for _ in range(5)]

        new_char_fields = []
        for i, instance in enumerate(instances):
            new_char_fields.append(create_random_string())
            instance.title = new_char_fields[i]
            instance.save(using=settings.STUDIO_DB)

        base_instances = models.Change.objects.bulk_stage_updated(instances, self.request)

        for i, base_instance in enumerate(base_instances):
            self.assertEqual(base_instance.char_field, new_char_fields[i])

    def test_bulk_stage_deleted(self):
        ...

    def test_get_for_model(self):
        content_type = models._get_content_type(model=BasicModel)

        # TODO: Is it safe to use the previously created change instances from previous testing?
        changes = models.Change.objects.get_for_model(BasicModel, request=None)

        for change in changes:
            self.assertFalse(change.committed)
            self.assertEqual(content_type, change.content_type)

        changes = models.Change.objects.get_for_model(BasicModel, request=None)

        for change in changes:
            self.assertTrue(change.committed)
            self.assertEqual(content_type, change.content_type)

    def test_get_for_instance(self):
        ...


class ChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@ModuleLevelFunctionTests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.request = RequestFactory()
        self.request.user = self.user

    def test__get_instance(self):
        new_instance = create_instance(user=self.user)
        base_instance = models.Change.objects.stage_created(new_instance, self.request)

        changes = models.Change.objects.get_for_instance(base_instance)
        change = changes.last()

        instance = change._get_instance(using=settings.STUDIO_DB, base=True)
        self.assertEqual(instance, base_instance)

        instance = change._get_instance(using=settings.STUDIO_DB, base=False)
        self.assertEqual(instance, new_instance)

    @create_test_user
    def test_commit(self, user):
        new_instance = create_instance(user=user)
        change, base_instance = models.Change.objects._create_change(
            models.STAGE_CREATED,
            new_instance,
            self.request,
            parent=None,
        )
        change.commit()

        related_instance = create_instance(user=user)
        change, base_related_instance = models.Change.objects._create_change(
            models.STAGE_CREATED,
            related_instance,
            self.request,
            parent=None,
        )
        change.commit()

        base_instance.one_to_one_field = base_related_instance
        base_instance.save(using=settings.STUDIO_DB)
        change, base_instance = models.Change.objects._create_change(
            models.STAGE_UPDATED,
            base_instance,
            self.request,
            parent=None
        )
        change.commit()

        base_instance.many_to_many_field.set([base_related_instance])
        change, base_instance = models.Change.objects._create_change(
            models.STAGE_UPDATED,
            base_instance,
            self.request,
            parent=None
        )
        change.commit()

        instance_on_studio_db = get_object_or_404(
            BasicModel.objects.using(settings.STUDIO_DB),
            id=base_instance.id
        )
        instance_on_main_site_db = get_object_or_404(
            BasicModel.objects.using(settings.MAIN_SITE_DB),
            id=base_instance.id
        )

        self.assertEqual(instance_on_studio_db, instance_on_main_site_db)

    def test_revert(self):
        ...

    def test_set_reverted(self):
        ...


class TrackedModelTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@ModuleLevelFunctionTests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.request = RequestFactory()
        self.request.user = self.user

    @create_test_user
    def atest_delete(self, user):
        new_instance = create_instance(user=user)
        time.sleep(2)
        new_instance.delete(fake=True)

        self.assertIsNotNone(new_instance.id)
        self.assertFalse(new_instance.tracked)

        time.sleep(2)
        new_instance.delete(fake=False)

        self.assertIsNone(new_instance.id)


class ChangeGroupManagerTests(TestCase):
    multi_db = True

    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@ModuleLevelFunctionTests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.request = RequestFactory()
        self.request.user = self.user

    def test__commit_changes(self):
        ...

    @create_test_user
    def test_publish(self, user):
        new_instance = create_instance(user=user)
        base_instance = models.Change.objects.stage_created(new_instance, self.request)

        new_title = create_random_string()
        base_instance.title = new_title
        base_instance.save(using=settings.STUDIO_DB)
        base_instance = models.Change.objects.stage_updated(base_instance, self.request)

        new_description = create_random_string(k=128)
        base_instance.description = new_description
        base_instance.save(using=settings.STUDIO_DB)
        base_instance = models.Change.objects.stage_updated(base_instance, self.request)

        response = models.ChangeGroup.objects.publish(base_instance, self.request)

        self.assertTrue(response['published'])

        # Quickly make sure the ``published`` is ``False`` if an instance that has
        # no related change instances is given to the ``publish`` method.
        response = models.ChangeGroup.objects.publish(create_instance(user=user), request=self.request)
        self.assertFalse(response['published'])

    @create_test_user
    def test_bulk_commit(self, user):
        new_instance = create_instance(user=user)
        base_instance = models.Change.objects.stage_created(new_instance, self.request)

        new_title = create_random_string()
        base_instance.title = new_title
        base_instance.save(using=settings.STUDIO_DB)
        base_instance = models.Change.objects.stage_updated(base_instance, self.request)

        new_description = create_random_string(k=128)
        base_instance.description = new_description
        base_instance.save(using=settings.STUDIO_DB)
        base_instance = models.Change.objects.stage_updated(base_instance, self.request)

        changes = models.Change.objects.get_for_instance(base_instance, committed=False)
        change_ids = [c.id for c in changes.order_by('date_created')]

        response = models.ChangeGroup.objects.bulk_commit(changes, self.request)
        changes_committed = response['change_group'].changes_committed.all()

        self.assertTrue(response['published'])
        self.assertEqual([c.id for c in changes_committed.order_by('date_created')], change_ids)

        response = models.ChangeGroup.objects.bulk_commit([], request=self.request)
        self.assertFalse(response['published'])


class ChangeGroupTests(TestCase):
    def setUp(self):
        ...
