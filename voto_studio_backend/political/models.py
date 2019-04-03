from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.translation import ugettext_lazy as _

from shared.utils import hidden_fields
from voto_studio_backend.changes.models import TrackedWorkshopModel
from voto_studio_backend.forms.models import (
    JSONModel, JSONAutoField, JSONCharField, JSONTextField, JSONChoiceField,
)
from voto_studio_backend.corruption.models import FinancialItem
from voto_studio_backend.media.models import Image


CATEGORIES = (
    ('1', _('Economy')),
    ('2', _('Agriculture')),
    ('3', _('Employment')),
    ('4', _('Transport')),
    ('5', _('Energy')),
    ('6', _('Waste Management')),
    ('7', _('Indigenous Relations')),
    ('8', _('Health Services')),
    ('9', _('Pensions')),
    ('10', _('Security')),
    ('11', _('Emergency Services')),
    ('12', _('Education')),
    ('13', _('Poverty')),
    ('14', _('Business')),
    ('15', _('Industry')),
    ('16', _('Entertainment')),
    ('17', _('None')),
)


INDIVIDUAL_TYPES = (
    ('1', _('Politician')),
    ('2', _('Business person')),
    ('3', _('Civilian')),
    ('4', _('Alcalde')),
    ('5', _('Ministro')),
    ('6', _('Presidente')),
    ('7', _('Vicepresidente')),
    ('8', _('Concejal')),
    ('9', _('Representante')),
    ('10', _('Gobierno')),
    ('11', _('Magistrado de la CSJ')),
    ('12', _('Magistrado Tribunal de Cuentas')),
    ('13', _('Diputado')),
    ('14', _('Vicealcalde')),
)


ORGANIZATION_TYPES = (
    ('1', _('Governmental')),
    ('2', _('Political Party')),
    ('3', _('Company')),
    ('4', _('Organización Sin Fines de Lucro')),
)

ELECTORAL_PERIODS = (
    ('1419', '2014-2019'),
    ('0914', '2009-2014'),
    ('0409', '2004-2009'),
    ('9904', '1999-2004'),
    ('9499', '1994-1999'),
)


POLITICAL_POSITIONS = (
    ('1', 'Presidente'),
    ('2', 'Diputado'),
    ('3', 'Representante'),
    ('4', 'Alcalde'),
    ('5', 'Gobernador'),
)


class Law(TrackedWorkshopModel):
    """
    Specifically a class created for individuals with previous political history.
    This can be mapped to them to see their effectiveness in the
    National Assembly or what were the interests of the laws they created, or whom did they affect.
    """
    code = models.CharField(_('Law Code'), max_length=256, blank=True, null=True)
    brief_description = models.CharField(_('Brief Description'), max_length=2048, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    category = models.CharField(_('Category'), choices=CATEGORIES, max_length=140, blank=True, null=True)

    table_descriptors = (
        'code',
        'brief_description',
        'category',
    )

    detail_descriptors = {
        'basic': (
            'code',
            'brief_description',
            'long_description',
            'category',
        ),
        'related': (),
    }

    read_only_fields = (
        'date_created',
        'user',
        'corruption_related_funds',
        'non_corruption_related_funds',
    )

    search_fields = (
        'brief_description',
        'category',
        'user__email',
    )

    search_autocomplete_field = 'brief_description'


class Experience(JSONModel):
    id = JSONAutoField(unique=True)
    type = JSONChoiceField(choices=CATEGORIES)
    title = JSONCharField(max_length=128)
    organization = JSONCharField(max_length=128)
    description = JSONTextField()


class Individual(TrackedWorkshopModel):
    related_name = 'individuals'

    name = models.CharField(_('Name'), max_length=128, default=str)
    alias = models.CharField(_('Alias'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    email = models.CharField(_('Email Address'), max_length=64, default=str)
    phone_number = models.CharField(_('Phone Number'), max_length=64, default=str)
    website = models.URLField(_('Website'), max_length=2048, blank=True, null=True)
    twitter_username = models.CharField(_('Twitter Username'), max_length=15, default=str)
    facebook_username = models.CharField(_('Facebook Username'), max_length=128, default=str)
    instagram_username = models.CharField(_('Instagram Username'), max_length=128, default=str)
    type = models.CharField(_('Type'), choices=INDIVIDUAL_TYPES, max_length=128, blank=True, null=True)
    related_funds = models.FloatField(blank=True, null=True, default=float)
    experience = JSONField(default=Experience(), blank=True, null=True)

    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)
    individuals = models.ManyToManyField('self', blank=True, related_name=related_name)
    laws = models.ManyToManyField('political.Law', blank=True, related_name=related_name)
    controversies = models.ManyToManyField('political.Controversy', blank=True, related_name=related_name)
    promises = models.ManyToManyField('political.Promise', blank=True, related_name=related_name)
    achievements = models.ManyToManyField('political.Achievement', blank=True, related_name=related_name)

    table_descriptors = (
        'name',
        'brief_description',
        'type',
    )

    detail_descriptors = {
        'basic': (
            'name',
            'brief_description',
            'long_description',
            'alias',
            'email',
            'phone_number',
            'website',
            'facebook_page',
            'corruption_related_funds',
            'non_corruption_related_funds',
        ),
        'related': (),
    }

    read_only_fields = (
        'date_created',
        'user',
        'corruption_related_funds',
        'non_corruption_related_funds',
    )

    search_fields = (
        'name',
        'alias',
        'brief_description',
        'email',
        'type',
        'user__email',
    )

    hidden_fields = hidden_fields(fields_tuple=('source',))

    search_method_fields = (
        'campaigns',
        'related_funds',
    )

    search_autocomplete_field = 'name'

    def get_campaigns(self):
        campaigns = get_list_or_404(Campaign, id__in=self.rels_dict['campaigns']['rels'])

        response = []
        for campaign in campaigns:
            response.append({
                'type': campaign.get_type_display(),
                'reelection': campaign.reelection,
            })

        return response

    def get_related_funds(self):
        instance = get_object_or_404(self._meta.model.objects.using(settings.MAIN_SITE_DB), id=self.id)
        financial_items = FinancialItem.objects \
            .using(settings.MAIN_SITE_DB) \
            .filter(id__in=instance.rels_dict['financial_items']['rels'])

        total = 0
        for financial_item in financial_items:
            total += financial_item.amount

        return total


class Campaign(TrackedWorkshopModel):
    related_name = 'campaigns'

    type = models.CharField(_('Type'), choices=INDIVIDUAL_TYPES, max_length=128, blank=True, null=True)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    reelection = models.BooleanField(_('Running for Reelection'), default=False)

    individuals = models.ManyToManyField('political.Individual', blank=True, related_name=related_name)

    table_descriptors = (
        'type',
        'brief_description',
        'reelection'
    )

    detail_descriptors = {
        'basic': (
            'type'
            'brief_description',
            'long_description',
            'reelection'
        ),
        'related': (),
    }

    search_fields = (
        'type'
        'brief_description',
        'long_description',
        'reelection'
        'user__email',
    )

    search_autocomplete_field = 'brief_description'

    hidden_fields = hidden_fields(fields_tuple=('source',))


class Organization(TrackedWorkshopModel):
    related_name = 'organizations'

    name = models.CharField(_('Name'), max_length=2048, default=str)
    alias = models.CharField(_('Alias'), max_length=64, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    email = models.CharField(_('Email Address'), max_length=64, default=str)
    phone_number = models.CharField(_('Phone Number'), max_length=64, default=str)
    website = models.URLField(_('Website'), max_length=2048, blank=True, null=True)
    twitter_username = models.CharField(_('Twitter Username'), max_length=15, default=str)
    facebook_username = models.CharField(_('Facebook Username'), max_length=128, default=str)
    instagram_username = models.CharField(_('Instagram Username'), max_length=128, default=str)
    type = models.CharField(_('Type'), choices=ORGANIZATION_TYPES, max_length=128, blank=True, null=True)
    related_funds = models.FloatField(blank=True, null=True, default=float)

    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)
    organizations = models.ManyToManyField('self', blank=True, related_name=related_name)
    individuals = models.ManyToManyField('political.Individual', blank=True, related_name=related_name)
    informative_snippets = models.ManyToManyField(
        'corruption.InformativeSnippet', blank=True, related_name=related_name)
    corruption_cases = models.ManyToManyField('corruption.CorruptionCase', blank=True, related_name=related_name)
    controversies = models.ManyToManyField('political.Controversy', blank=True, related_name=related_name)
    promises = models.ManyToManyField('political.Promise', blank=True, related_name=related_name)
    achievements = models.ManyToManyField('political.Achievement', blank=True, related_name=related_name)

    table_descriptors = (
        'name',
        'brief_description',
        'type',
    )

    detail_descriptors = {
        'basic': (
            'name',
            'brief_description',
            'long_description',
            'alias',
            'email',
            'phone_number',
            'website',
            'facebook_page',
            'corruption_related_funds',
            'non_corruption_related_funds',
        ),
        'related': (),
    }

    hidden_fields = hidden_fields(fields_tuple=('source',))

    search_fields = (
        'name',
        'alias',
        'brief_description',
        'email',
        'type',
        'user__email',
    )

    search_method_fields = (
        'related_funds',
    )

    search_autocomplete_field = 'name'

    def get_related_funds(self):
        instance = get_object_or_404(self._meta.model.objects.using(settings.MAIN_SITE_DB), id=self.id)
        financial_items = FinancialItem.objects \
            .using(settings.MAIN_SITE_DB) \
            .filter(id__in=instance.rels_dict['financial_items']['rels'])

        total = 0
        for financial_item in financial_items:
            total += financial_item.amount

        return total


class Promise(TrackedWorkshopModel):
    title = models.CharField(_('Title'), max_length=2048, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    type = models.CharField(_('Type'), choices=CATEGORIES, max_length=128, blank=True, null=True)
    fulfilled = models.BooleanField(default=False)

    table_descriptors = (
        'brief_description',
        'type',
        'fulfilled',
    )

    detail_descriptors = {
        'basic': (
            'brief_description',
            'type',
            'fulfilled',
        ),
        'related': (),
    }

    search_fields = (
        'brief_description',
        'type',
        'user__email',
    )

    search_method_fields = (
        'individuals',
    )

    search_autocomplete_field = 'title'

    def get_individuals(self):
        individuals = get_list_or_404(Individual, id__in=self.rels_dict['individuals']['rels'])

        response = []
        for individual in individuals:
            order = individual.order
            if len(order['images']):
                primary_image_url = get_object_or_404(Image, id=order['images'][0]).image.url
            else:
                primary_image_url = None

            response.append({
                'id': individual.id,
                'name': individual.name,
                'primary_image_url': primary_image_url,
            })

        return response


class Achievement(TrackedWorkshopModel):
    title = models.CharField(_('Title'), max_length=2048, default=str)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    type = models.CharField(_('Type'), choices=CATEGORIES, max_length=128, blank=True, null=True)

    table_descriptors = (
        'brief_description',
        'type',
    )

    detail_descriptors = {
        'basic': (
            'brief_description',
            'type',
        ),
        'related': (),
    }

    search_fields = (
        'brief_description',
        'type',
        'user__email',
    )

    search_method_fields = (
        'individuals',
    )

    search_autocomplete_field = 'title'

    def get_individuals(self):
        individuals = get_list_or_404(Individual, id__in=self.rels_dict['individuals']['rels'])

        response = []
        for individual in individuals:
            order = individual.order
            if len(order['images']):
                primary_image_url = get_object_or_404(Image, id=order['images'][0]).image.url
            else:
                primary_image_url = None

            response.append({
                'id': individual.id,
                'name': individual.name,
                'primary_image_url': primary_image_url,
            })

        return response


class Controversy(TrackedWorkshopModel):
    title = models.CharField(_('Title'), max_length=2048, default=str)
    brief_description = models.CharField(_('Description'), max_length=2048, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    type = models.CharField(_('Type'), choices=CATEGORIES, max_length=128, blank=True, null=True)

    table_descriptors = (
        'brief_description',
        'type',
    )

    detail_descriptors = {
        'basic': (
            'brief_description',
            'type',
        ),
        'related': (),
    }

    search_fields = (
        'brief_description',
        'type',
        'user__email',
    )

    search_method_fields = (
        'individuals',
    )

    search_autocomplete_field = 'title'

    def get_individuals(self):
        individuals = get_list_or_404(Individual, id__in=self.rels_dict['individuals']['rels'])

        response = []
        for individual in individuals:
            order = individual.order
            if len(order['images']):
                primary_image_url = get_object_or_404(Image, id=order['images'][0]).image.url
            else:
                primary_image_url = None

            response.append({
                'id': individual.id,
                'name': individual.name,
                'primary_image_url': primary_image_url,
            })

        return response

    class Meta:
        verbose_name_plural = 'Controversies'
