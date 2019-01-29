import random
import string

from django.conf import settings
from django.db import models
from django.utils import timezone
from voto_backend.changes.models import TrackedModel
from voto_backend.forms.models import InfoMixin
from voto_backend.search.models import IndexingMixin


TEST_CHOICES = (
    ('1', 'One'),
    ('2', 'Two'),
    ('3', 'Three'),
)


def create_random_string(k=15, seed='test_seed'):
    random.seed(seed)

    return ''.join(random.choices(string.ascii_letters, k=k))


class BasicModelManager(models.Manager):
    def create_with_defaults(self, user):
        basic_model = self.model(
            char_field=create_random_string(),
            text_field=create_random_string(k=128),
            integer_field=random.randint(0, 100),
            float_field=random.random(),
            boolean_field=random.choice([True, False]),
            url_field=f'https://www.{create_random_string()}.com/',
            choice_field=random.choice(TEST_CHOICES)[0],
            user=user,
        )
        basic_model.save(using=settings.STUDIO_DB)

        return basic_model


class BasicModel(TrackedModel, InfoMixin, IndexingMixin):
    char_field = models.CharField(max_length=128, blank=True, default=str)
    text_field = models.TextField(blank=True, default=str)
    integer_field = models.IntegerField(blank=True, default=int)
    float_field = models.FloatField(blank=True, default=float)
    boolean_field = models.BooleanField(default=False)
    url_field = models.URLField(blank=True, default=str)
    one_to_one_field = models.OneToOneField('self', null=True, on_delete=models.SET_NULL)
    foreign_key_field = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='basic_models')
    many_to_many_field = models.ManyToManyField('self')
    choice_field = models.CharField(max_length=128, choices=TEST_CHOICES, blank=True, null=True)
    date_time_field = models.DateTimeField(blank=True, default=timezone.now)

    objects = BasicModelManager()

    basic_field_count = 10
    related_field_count = 1

    table_descriptors = (
        'char_field',
    )

    detail_descriptors = {
        'basic': (),
        'related': (),
    }