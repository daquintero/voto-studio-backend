import random
import string

from django.db import models
from django.utils import timezone

from shared.utils import hidden_fields
from voto_studio_backend.changes.models import TrackedWorkshopModelManager, TrackedWorkshopModel


TEST_CHOICES = (
    ('1', 'One'),
    ('2', 'Two'),
    ('3', 'Three'),
)


def create_random_string(k=15, seed='test_seed'):
    random.seed(seed)

    return ''.join(random.choices(string.ascii_letters, k=k))


class BasicModelManager(TrackedWorkshopModelManager):
    def create_with_defaults(self, user):
        basic_model = super().create(
            char_field=create_random_string(),
            text_field=create_random_string(k=128),
            integer_field=random.randint(0, 100),
            float_field=random.random(),
            boolean_field=random.choice([True, False]),
            url_field=f'https://www.{create_random_string()}.com/',
            choice_field=random.choice(TEST_CHOICES)[0],
            user=user,
        )

        return basic_model


class BasicModel(TrackedWorkshopModel):
    related_name = 'basic_models'

    # Basic Fields
    char_field = models.CharField(max_length=128, blank=True, default=str)
    text_field = models.TextField(blank=True, default=str)
    integer_field = models.IntegerField(blank=True, default=int)
    float_field = models.FloatField(blank=True, default=float)
    boolean_field = models.BooleanField(default=False)
    url_field = models.URLField(blank=True, default=str)
    choice_field = models.CharField(max_length=128, choices=TEST_CHOICES, blank=True, null=True)
    date_time_field = models.DateTimeField(blank=True, default=timezone.now)
    one_to_one_field = models.OneToOneField('self', null=True, on_delete=models.SET_NULL)
    foreign_key_field = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name=related_name)

    # Related Fields
    many_to_many_field = models.ManyToManyField('self', related_name=related_name)

    objects = BasicModelManager()

    # This model has 10 basic fields, but it
    # inherits from ``TrackedWorkshopModel``
    # which adds a further 3.
    # TODO: Include hidden fields
    basic_field_count = 10 + 3

    # This model has 1 related field, although
    # ``TrackedWorkshopModel`` adds 3 they are
    # not counted as related fields as they are
    # only relevant to the media app.
    related_field_count = 1

    table_descriptors = (
        'char_field',
    )

    detail_descriptors = {
        'basic': (),
        'related': (),
    }

    search_autocomplete_field = 'char_field'

    hidden_fields = hidden_fields(fields_tuple=('order', 'views', 'location', 'location_id_name', 'location_id',))
