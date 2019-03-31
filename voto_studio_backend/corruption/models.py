from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shared.utils import hidden_fields
from voto_studio_backend.changes.models import TrackedWorkshopModel


class InformativeSnippet(TrackedWorkshopModel):
    """
    The basic source of information that can map to other relationships, with separate images, etc.
    An informative snippet is basically a small piece of news that can be related on the grand scheme of things.
    """
    related_name = 'informative_snippets'

    title = models.CharField(_('Title'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)

    twitter_feed = models.URLField(_('Twitter Feed URL'), blank=True, null=True)

    corruption_cases = models.ManyToManyField('corruption.CorruptionCase', blank=True, related_name=related_name)
    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)
    individuals = models.ManyToManyField('political.Individual', blank=True, related_name=related_name)
    laws = models.ManyToManyField('political.Law', blank=True, related_name=related_name)
    controversies = models.ManyToManyField('political.Controversy', blank=True, related_name=related_name)
    informative_snippets = models.ManyToManyField('self', blank=True, related_name=related_name)

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

    search_fields = (
        'title',
        'brief_description',
        'user__email',
    )


class CorruptionCase(TrackedWorkshopModel):
    """
    A corruption case is basically an ongoing probably months old case that can
    have different corruption evidence moments related to it, which are the mapped
    corruption instances. Similarly, it is still possible to map everything else.
    """
    related_name = 'corruption_cases'

    title = models.CharField(_('Title'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)

    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)
    controversies = models.ManyToManyField('political.Controversy', blank=True, related_name=related_name)
    individuals = models.ManyToManyField('political.Individual', blank=True, related_name=related_name)
    laws = models.ManyToManyField('political.Law', blank=True, related_name=related_name)
    corruption_cases = models.ManyToManyField('self', blank=True, related_name=related_name)

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

    search_fields = (
        'title',
        'brief_description',
        'user__email',
    )

    hidden_fields = hidden_fields(fields_tuple=('source',))


class FinancialItem(TrackedWorkshopModel):
    """
    Gives a small description and amount similar to fields on an excel describing a tally of money
    related to an informative snippets. Operations can be done to calculate the total money sent related to informative
    snippets or corruption events.
    """
    title = models.CharField(_('Title'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    amount = models.FloatField(_('Amount'), blank=True, default=float)

    table_descriptors = (
        'title',
        'amount',
        'source',
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

    search_fields = (
        'title',
        'brief_description',
        'user__email',
    )

    search_method_fields = (
        'table_values',
    )
