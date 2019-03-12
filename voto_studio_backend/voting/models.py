from django.contrib.postgres.fields import JSONField
from django.db import models

from shared.utils import hidden_fields
from voto_studio_backend.changes.models import TrackedWorkshopModel
from voto_studio_backend.forms.models import JSONModel, JSONAutoField, JSONCharField


class References(JSONModel):
    id = JSONAutoField()
    text = JSONCharField(max_length=2048)
    source = JSONCharField(max_length=2048)


class Tutorial(TrackedWorkshopModel):
    related_name = 'tutorials'

    title = models.CharField(max_length=128, blank=True, null=True)
    summary = models.CharField(max_length=140, blank=True, null=True)
    body = models.TextField(blank=True)
    references = JSONField(default=References())

    table_descriptors = (
        'title',
        'summary',
    )

    detail_descriptors = {
        'basic': (),
        'related': (),
    }

    search_fields = (
        'title',
        'summary',
        'body',
    )

    hidden_fields = hidden_fields(fields_tuple=('location', 'date', 'source', 'statistics'))
