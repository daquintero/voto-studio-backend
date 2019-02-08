from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

TWITTER_TYPES = (
    ('1', _('Hashtag')),
    ('2', _('Profile')),
)


class Image(models.Model):
    title = models.CharField(max_length=2048, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    date_uploaded = models.DateTimeField(default=now)

    table_descriptors = (
        'name',
    )

    detail_descriptors = {
        'basic': (
            'name',
        ),
        'related': (
            {'field': 'user', 'attrs': ('name', 'email',)},
        ),
    }

    def __str__(self):
        return f'{self.id} <{self.title}>'


class Video(models.Model):
    title = models.CharField(default=str, max_length=32, blank=True)
    embed_url = models.URLField(max_length=2048, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    date_uploaded = models.DateTimeField(default=now)

    table_descriptors = (
        'title',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'embed_url',
        ),
        'related': (),
    }

    def __str__(self):
        return f'{self.id} <{self.title}>'


class Resource(models.Model):
    title = models.CharField(default=str, max_length=32, blank=True)
    brief_description = models.CharField(default=str, max_length=128)
    icon = models.CharField(default=str, max_length=32, blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    link = models.URLField(max_length=2048, blank=True)
    voting_resource = models.BooleanField(default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    date_uploaded = models.DateTimeField(default=now)

    table_descriptors = (
        'title',
        'icon',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'icon',
            'voting_resource',
        ),
        'related': (),
    }

    def __str__(self):
        return f'{self.id} <{self.title}>'
