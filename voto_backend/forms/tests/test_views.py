import json
import random
import time

from django.conf import settings
from django.db.models.fields import CharField, FloatField, IntegerField
from django.shortcuts import get_object_or_404
from django.test import TestCase, RequestFactory, TransactionTestCase
from django.urls import reverse
from shared.testing.test_app.models import BasicModel, TEST_CHOICES, create_random_string
from shared.testing.es_test_cases import ESTestCase
from shared.testing.utils import create_test_user, auth_header, get_field, create_instance
from .. import views
from voto_backend.changes.models import Change
from voto_backend.users.models import User


class ModelListTests(ESTestCase):
    @create_test_user
    def test_get(self, user):
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(user)
        response = self.client.get(reverse('forms:list'))
        items = response.data['items']

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(items))
        self.assertEqual(len(items), len(settings.WORKSHOP_MODELS))


class ModuleLevelFunctionTests(ESTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@ModuleLevelFunctionTests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.request = RequestFactory()
        self.request.user = self.user
        self.instance = create_instance(user=self.user)

    def test_get_name(self):
        fields = self.instance._meta.get_fields()

        one_to_one_field = get_field('one_to_one_field', fields)
        many_to_many_field = get_field('many_to_many_field', fields)

        self.assertEqual(views.get_name(one_to_one_field), 'one_to_one_field')
        self.assertEqual(views.get_name(many_to_many_field), 'many_to_many_field')

    def test_get_field_value(self):
        related_instance = create_instance(user=self.user)
        self.instance.many_to_many_field.add(related_instance)

        many_to_many_field = BasicModel._meta.get_field('many_to_many_field')

        self.assertEqual(list(views.get_field_value(self.instance, many_to_many_field).all()), [related_instance])
        self.assertEqual(list(views.get_field_value(related_instance, many_to_many_field).all()), [self.instance])

        self.instance.many_to_many_field.remove(related_instance)
        self.assertFalse(views.get_field_value(self.instance, many_to_many_field).all())

    def test_get_field_type(self):
        self.assertEqual(views.get_field_type(CharField()), 'text')
        self.assertEqual(views.get_field_type(CharField(choices=(('', '')))), 'select')
        self.assertEqual(views.get_field_type(FloatField()), 'number')

    def test_get_related_instances(self):
        random.seed('ModuleLevelFunctionTests::test_get_related_instances')

        self.assertEqual(views.get_related_instances(None, None), {'instances': [], 'table_heads': []})

        many_to_many_field = self.instance._meta.get_field('many_to_many_field')

        self.assertEqual(views.get_related_instances(self.instance, many_to_many_field)['instances'], [])

        related_instances = [create_instance(user=self.user) for _ in range(10)]
        # ElasticSearch is a "near-real-time (NRT)" search engine,
        # this means it can take up to about a second for newly
        # created indexes to become searchable. So we add a delay
        #  of two seconds to account for this NRT behaviour.
        time.sleep(2)
        sample_size = random.randint(0, 10)
        self.instance.many_to_many_field.set(random.sample(related_instances, k=sample_size))
        related_results = views.get_related_instances(self.instance, many_to_many_field)

        self.assertEqual(len(related_results['instances']), sample_size)

    def test_get_options(self):
        basic_model_instances = [create_instance(user=self.user) for _ in range(10)]
        # Again, add a delay  of two seconds
        # to account for NRT behaviour.
        time.sleep(2)
        field = self.instance._meta.get_field('one_to_one_field')
        options = views.get_options(self.instance, field)

        self.assertEqual(len(options['options']), len(basic_model_instances) + 1)

        self.instance.one_to_one_field = random.choice(basic_model_instances)
        self.instance.save()

        options = views.get_options(self.instance, field)

        self.assertEqual(len(options['options']), len(basic_model_instances))

        field = self.instance._meta.get_field('foreign_key_field')
        options = views.get_options(self.instance, field)

        self.assertEqual(len(options['options']), BasicModel.objects.count())

        field = self.instance._meta.get_field('choice_field')
        options = views.get_options(self.instance, field)

        self.assertEqual(len(options['options']), len(TEST_CHOICES) + 1)

    def test_get_or_create_instance(self):
        app_label, model_name = self.instance._meta.label.split('.')

        # We will use this method to get the instance
        # referenced by ``self.instance``.
        instance_id = self.instance.id
        model_class, (instance, new) = views.get_or_create_instance(app_label, model_name, instance_id, self.request)

        # Make sure that no new instance was created, the
        # instance retrieved is an instance of the correct
        # model_class and then the instance retrieved is
        # the correct instance object.
        self.assertFalse(new)
        self.assertIsInstance(self.instance, model_class)
        self.assertEqual(self.instance, instance)

        # We also want to test the "create" part of the
        # method. If we provide an ID that matches no
        # instance of the given type then it will create
        # a new instance. Therefore, by passing ``None``
        # as the ID a new instance will always be made.
        model_class, (instance, new) = views.get_or_create_instance(app_label, model_name, None, self.request)

        # Make sure that a new instance was made and confirm
        # it is an instance of the correct model class.
        self.assertTrue(new)
        self.assertIsInstance(instance, model_class)

    def test_is_read_only(self):
        field = BasicModel._meta.get_field('date_created')

        self.assertTrue(views.is_read_only(field))

    def test_parse_value(self):
        self.assertIsInstance(views.parse_value(FloatField(), int(random.randint(0, 100))), float)
        self.assertIsInstance(views.parse_value(IntegerField(), float(random.randint(0, 100))), int)
        self.assertIsInstance(views.parse_value(CharField(), create_random_string()), str)

    def test_get_basic_fields(self):
        basic_fields = views.get_basic_fields(model=BasicModel)

        self.assertEqual(len(basic_fields), BasicModel.basic_field_count)

        basic_fields = views.get_basic_fields(instance=self.instance)

        self.assertEqual(len(basic_fields), BasicModel.basic_field_count)


class BuildFormAPITests(ESTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@BuildFormAPITests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(self.user)
        self.instance = create_instance(user=self.user)

    def test_get(self):
        # Make the same GET request as the frontend would.
        response = self.client.get(reverse('forms:build'), {
            'al': 'test_app',
            'mn': 'basicmodel',
            'id': 'new',
        })
        form_data = response.data['form']

        # Make sure the request was successful with a 200
        # HTTP code. Make sure we have created a new instance
        # by checking ``new``. Make sure the correct model
        # was used to build the form. Check the number of
        # each type of field against known values to check
        # whether the correct fields have been provided.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form_data['new'])
        self.assertEqual(form_data['parent_model']['model_label'], 'test_app.BasicModel')
        self.assertEqual(len(form_data['basic_fields']), BasicModel.basic_field_count)
        self.assertEqual(len(form_data['related_fields']), BasicModel.related_field_count)
        self.assertEqual(form_data['default_values'], {})

        # Perform the same GET request as before but this
        # time supply an ID that exists so we can build a
        # form with default values.
        response = self.client.get(reverse('forms:build'), {
            'al': 'test_app',
            'mn': 'basicmodel',
            'id': self.instance.id,
        })
        form_data = response.data['form']

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form_data['new'])
        self.assertEqual(form_data['parent_model']['model_label'], 'test_app.BasicModel')
        self.assertEqual(len(form_data['basic_fields']), BasicModel.basic_field_count)
        self.assertEqual(len(form_data['related_fields']), BasicModel.related_field_count)
        self.assertNotEqual(form_data['default_values'], {})


class RelatedFieldsAPITests(ESTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@RelatedFieldsAPITests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(self.user)
        self.instance = create_instance(user=self.user)
        self.related_instances = [create_instance(user=self.user) for _ in range(10)]
        time.sleep(2)

    def test_get(self):
        response = self.client.get(reverse('forms:get_related_fields'), {
            # Parent model class info
            'pal': 'test_app',
            'pmn': 'basicmodel',
            'pid': 'new',
            # Related model class info
            'ral': 'test_app',
            'rmn': 'basicmodel',
            'rfn': 'many_to_many_field',
            # Meta
            'page_size': 100,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['verbose_name'], BasicModel._meta.verbose_name)
        self.assertEqual(len(response.data['related_field_instances']), len(self.related_instances) + 1)

        random.seed('RelatedFieldsAPITests::test_get')
        num_related_instances = random.randint(1, len(self.related_instances))
        random_related_instances = random.sample(self.related_instances, k=num_related_instances)
        self.instance.many_to_many_field.set(random_related_instances)

        response = self.client.get(reverse('forms:get_related_fields'), {
            # Parent model class info
            'pal': 'test_app',
            'pmn': 'basicmodel',
            'pid': self.instance.id,
            # Related model class info
            'ral': 'test_app',
            'rmn': 'basicmodel',
            'rfn': 'many_to_many_field',
            # Meta
            'page_size': 100,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['verbose_name'], BasicModel._meta.verbose_name)
        self.assertEqual(len(response.data['related_field_instances']),
                         len(self.related_instances) - num_related_instances)


class InstanceDetailAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@InstanceDetailAPITests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(self.user)
        self.instance = create_instance(user=self.user)

    def test_get(self):
        response = self.client.get(reverse('forms:detail'), {
            'al': 'test_app',
            'mn': 'basicmodel',
            'id': self.instance.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['item']['id'], self.instance.id)


class UpdateBasicFieldsAPITests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@UpdateBasicFieldsAPITests.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(self.user)
        self.instance = create_instance(user=self.user)
        self.seed = 'UpdateBasicFieldsAPITests'

    def test_post(self):
        random.seed(self.seed)
        related_instance = create_instance(user=self.user)
        new_data = {
            'char_field': create_random_string(seed=self.seed),
            'text_field': create_random_string(k=400, seed=self.seed),
            'boolean_field': random.choice([True, False]),
            'choice_field': {'value': random.choice(TEST_CHOICES)[0]},
            'one_to_one_field': {'value': related_instance.id},
            'foreign_key_field': {'value': related_instance.id},
        }

        response = self.client.post(reverse('forms:update_basic_fields'), {
            'model_label': 'test_app.BasicModel',
            'id': self.instance.id,
            'values': json.dumps(new_data),
        })

        updated_instance = get_object_or_404(BasicModel, id=self.instance.id)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['result']['updated'])
        self.assertEqual(updated_instance.char_field, new_data['char_field'])
        self.assertEqual(updated_instance.text_field, new_data['text_field'])
        self.assertEqual(updated_instance.boolean_field, new_data['boolean_field'])
        self.assertEqual(updated_instance.choice_field, new_data['choice_field']['value'])
        self.assertEqual(updated_instance.one_to_one_field.id, new_data['one_to_one_field']['value'])

        # As you can't set an instance as a OneToOne if it is
        # already a member of a OneToOne relationship we should
        # test this case. Even though the user shouldn't be able
        # to trigger this error as any instances that are already
        # in a OneToOne relationship are omitted from the choices
        # of instances in a OneToOne select box, we should still
        # check this by making a bad request.
        extra_related_instance = create_instance(user=self.user)
        related_instance.one_to_one_field = extra_related_instance
        related_instance.save(using=settings.STUDIO_DB)

        response = self.client.post(reverse('forms:update_basic_fields'), {
            'model_label': 'test_app.BasicModel',
            'id': self.instance.id,
            'values': json.dumps({
                'one_to_one_field': {'value': extra_related_instance.id},
            }),
        })

        # Make sure we get a 400 HTTP code rather
        # than a 500 server error.
        self.assertEqual(response.status_code, 400)


class UpdateRelatedFieldAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@UpdateRelatedFieldAPITest.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(self.user)
        self.instance = create_instance(user=self.user)

    def test_post(self):
        random.seed('UpdateRelatedFieldAPITests::test_post')
        related_instance = create_instance(user=self.user)
        response = self.client.post(reverse('forms:update_related_field'), {
            'model_label': 'test_app.BasicModel',
            'id': self.instance.id,
            'related_model_label': 'test_app.BasicModel',
            'related_ids': [related_instance.id],
            'update_type': 'add',
            'field_name': 'many_to_many_field',
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(self.instance.many_to_many_field.all()), [related_instance])

        response = self.client.post(reverse('forms:update_related_field'), {
            'model_label': 'test_app.BasicModel',
            'id': self.instance.id,
            'related_model_label': 'test_app.BasicModel',
            'related_ids': [related_instance.id],
            'update_type': 'remove',
            'field_name': 'many_to_many_field',
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(self.instance.many_to_many_field.all()), [])


class PublishContentAPITests(ESTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @create_test_user
    def test_post(self, user):
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(user)
        request = self.factory.post(reverse('forms:publish'))
        request.user = user
        random.seed('PublishContentAPITests::test_post')

        instance = create_instance(user=user)
        base_instance = Change.objects.stage_created(instance, request)

        related_instance = create_instance(user=user)
        base_related_instance = Change.objects.stage_created(related_instance, request)

        changes = {
            'char_field': create_random_string(),
            'text_field': create_random_string(k=400),
            'one_to_one_field': base_related_instance,
            'foreign_key_field': base_related_instance,
            'many_to_many_field': base_related_instance,
        }

        base_instance.char_field = changes['char_field']
        base_instance = Change.objects.stage_updated(base_instance, request)

        base_instance.text_field = changes['text_field']
        base_instance = Change.objects.stage_updated(base_instance, request)

        base_instance.one_to_one_field = changes['one_to_one_field']
        base_instance = Change.objects.stage_updated(base_instance, request)

        base_instance.foreign_key_field = changes['foreign_key_field']
        base_instance = Change.objects.stage_updated(base_instance, request)

        base_instance.many_to_many_field.set([changes['many_to_many_field']])
        base_instance = Change.objects.stage_updated(base_instance, request)

        base_instance.save(using=settings.STUDIO_DB)

        time.sleep(2)
        response = self.client.post(reverse('forms:publish'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_email'], user.email)
        self.assertEqual(response.data['changes_committed_count'], len(changes)+2)


class DeleteInstanceAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='foo@UpdateRelatedFieldsAPITest.com',
            name='Baz',
            password='Foobarbaz123'
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = auth_header(self.user)
        self.instance = create_instance(user=self.user)

    def test_delete(self):
        response = self.client.delete(reverse('forms:delete_instance'), data=json.dumps({
            'app_label': 'test_app',
            'model_name': 'basicmodel',
            'id': self.instance.id,
        }), content_type='application/json')
        instance = get_object_or_404(BasicModel, id=response.data['item']['id'])

        self.assertTrue(response.status_code, 200)
        self.assertFalse(instance.tracked)
