from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from voto_backend.changes.models import TrackedWorkshopModel, hidden_fields


class InformativeSnippet(TrackedWorkshopModel):
    """
    The basic source of information that can map to other relationships, with separate images, etc.
    An informative snippet is basically a small piece of news that can be related on the grand scheme of things.
    """
    title = models.CharField(_('Title'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)

    twitter_feed = models.URLField(_('Twitter Feed URL'), blank=True, null=True)

    corruption_cases = models.ManyToManyField('corruption.CorruptionCase', blank=True)
    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True)
    individuals = models.ManyToManyField('political.Individual', blank=True)
    law = models.ManyToManyField('political.Law', blank=True)
    controversies = models.ManyToManyField('political.Controversy', blank=True)

    table_descriptors = (
        'title',
        'brief_description',
        'source',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'brief_description',
            'long_description',
            'source',
            'date_created',
        ),
        'related': (
            {'field': 'corruption_cases', 'attrs': ('title',)},
        ),
    }


class CorruptionCase(TrackedWorkshopModel):
    """
    A corruption case is basically an ongoing probably months old case that can
    have different corruption evidence moments related to it, which are the mapped
    corruption instances. Similarly, it is still possible to map everything else.
    """
    title = models.CharField(_('Title'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)

    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True)
    controversies = models.ManyToManyField('political.Controversy', blank=True)

    table_descriptors = (
        'title',
        'brief_description',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'brief_description',
            'long_description',
            'source',
            'date_created',
        ),
        'related': (),
    }

    hidden_fields = hidden_fields(('source',))


class FinancialItem(TrackedWorkshopModel):
    """
    Gives a small description and amount similar to fields on an excel describing a tally of money
    related to an informative snippets. Operations can be done to calculate the total money sent related to informative
    snippets or corruption events.
    """
    title = models.CharField(_('Title'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    amount = models.FloatField(_('Amount'), blank=True, default=float)
    corruption_related = models.BooleanField(default=False)

    table_descriptors = (
        'title',
        'brief_description',
        'amount',
        'corruption_related',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'brief_description',
            'amount',
            'source',
            'corruption_related',
        ),
        'related': (),
    }