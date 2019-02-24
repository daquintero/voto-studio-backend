from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shared.utils import hidden_fields
from voto_studio_backend.changes.models import TrackedWorkshopModel
from voto_studio_backend.forms.models import JSONModel, JSONAutoField, JSONCharField, JSONTextField

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
    code = models.CharField(_('Law Code'), max_length=128, blank=True, null=True)
    brief_description = models.CharField(_('Description'), max_length=128, blank=True, null=True)
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


class Experience(JSONModel):
    id = JSONAutoField(unique=True)
    type = JSONCharField(max_length=32)
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
    corruption_related_funds = models.FloatField(blank=True, null=True, default=float)
    non_corruption_related_funds = models.FloatField(blank=True, null=True, default=float)
    experience = JSONField(default=Experience(), blank=True, null=True)

    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)
    individuals = models.ManyToManyField('self', blank=True, related_name=related_name)
    laws = models.ManyToManyField('political.Law', blank=True, related_name=related_name)

    table_descriptors = (
        'name',
        'brief_description',
        'type',
        'corruption_related_funds',
        'non_corruption_related_funds',
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

    hidden_fields = hidden_fields(fields_tuple=('source',))


class Organization(TrackedWorkshopModel):
    related_name = 'organizations'

    name = models.CharField(_('Name'), max_length=2048, default=str, unique=True)
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
    corruption_related_funds = models.FloatField(blank=True, null=True, default=float)
    non_corruption_related_funds = models.FloatField(blank=True, null=True, default=float)

    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)
    organizations = models.ManyToManyField('self', blank=True, related_name=related_name)
    individuals = models.ManyToManyField('political.Individual', blank=True, related_name=related_name)

    table_descriptors = (
        'name',
        'brief_description',
        'type',
        'corruption_related_funds',
        'non_corruption_related_funds',
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


class Promise(TrackedWorkshopModel):
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    type = models.CharField(_('Type'), choices=CATEGORIES, max_length=128, blank=True, null=True)
    fulfilled = models.BooleanField(default=False)

    individual = models.ForeignKey('political.Individual', blank=True, null=True, on_delete=models.SET_NULL)

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


class Achievement(TrackedWorkshopModel):
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    type = models.CharField(_('Type'), choices=CATEGORIES, max_length=128, blank=True, null=True)

    individual = models.ForeignKey('political.Individual', blank=True, null=True, on_delete=models.SET_NULL)

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


class Controversy(TrackedWorkshopModel):
    brief_description = models.CharField(_('Description'), max_length=2048, blank=True, null=True)
    type = models.CharField(_('Type'), choices=CATEGORIES, max_length=128, blank=True, null=True)

    individual = models.ForeignKey('political.Individual', blank=True, null=True, on_delete=models.SET_NULL)
    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True)

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

    class Meta:
        verbose_name_plural = 'Controversies'


class ElectoralPeriod(TrackedWorkshopModel):
    related_name = 'electoral_periods'

    individual = models.ForeignKey('political.Individual', blank=True, null=True, on_delete=models.SET_NULL)
    brief_description = models.CharField(_('Description'), max_length=140, blank=True, null=True)
    long_description = models.TextField(_('Long Description'), blank=True, default=settings.TEXT_FIELD_DEFAULT)
    period = models.CharField(_('Period'), choices=ELECTORAL_PERIODS, max_length=128, blank=True, null=True)
    position = models.CharField(_('Position'), choices=POLITICAL_POSITIONS, max_length=128, blank=True, null=True)
    attendance_percentage = models.FloatField(_('Attendance Percentage'), blank=True, null=True, default=float)
    published_public_finances = models.BooleanField(_('Published Public Finances'), default=False)

    laws = models.ManyToManyField('political.Law', blank=True, related_name=related_name)
    financial_items = models.ManyToManyField('corruption.FinancialItem', blank=True, related_name=related_name)

    table_descriptors = (
        'period',
        'position',
        'attendance_percentage',
        'published_public_finances',
    )

    detail_descriptors = {
        'basic': (
            'brief_description',
            'long_description',
            'period',
            'position',
            'attendance_percentage',
            'published_public_finances'
        ),
        'related': (),
    }

    hidden_fields = hidden_fields(fields_tuple=('source',))
