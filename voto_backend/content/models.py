from django.db import models
from django.conf import settings
from voto_backend.changes.models import TrackedModel
from voto_backend.forms.models import InfoMixin
from voto_backend.search.models import IndexingMixin


TWITTER_TYPES = (
    ("hashtag", "Hashtag"),
    ("profile", "Perfil"),
)


class Image(TrackedModel, InfoMixin, IndexingMixin):
    name = models.CharField(max_length=30, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, blank=True)

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

    def get_absolute_image_url(self):
        return f'http://127.0.0.1:8000/media/{self.image}'

    def __str__(self):
        return f'{self.id} <{self.name}>'


class Logo(TrackedModel, InfoMixin, IndexingMixin):
    name = models.CharField(max_length=30, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, blank=True)

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

    def get_absolute_logo_url(self):
        return f'http://127.0.0.1:8000/media/{self.logo}'

    def __str__(self):
        return f'{self.id} <{self.name}>'


class IconData(TrackedModel, InfoMixin, IndexingMixin):
    title = models.CharField(default=str, max_length=20, blank=True)
    icon = models.CharField(default=str, max_length=40, blank=True)
    data = models.CharField(default=str, max_length=20, blank=True)
    link = models.URLField(max_length=256, blank=True, null=True)

    table_descriptors = (
        'title',
        'icon',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'icon',
            'data',
            'link',
        ),
        'related': (),
    }

    def __str__(self):
        return f'{self.id} <{self.title}>'


class Video(TrackedModel, InfoMixin, IndexingMixin):
    title = models.CharField(default=str, max_length=30, blank=True)
    embed_url_src = models.URLField(max_length=256, blank=True)

    table_descriptors = (
        'title',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'embed_url_src',
        ),
        'related': (),
    }

    def __str__(self):
        return f'{self.id} <{self.title}>'


class Resource(TrackedModel, InfoMixin, IndexingMixin):
    title = models.CharField(default=str, max_length=20, blank=True)
    icon = models.CharField(default=str, max_length=40, blank=True)
    file = models.FileField(upload_to='resources_fs/', blank=True, null=True)
    voting_resource = models.BooleanField(default=False)

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

    def get_absolute_file_url(self):
        return f'http://127.0.0.1:8000/media/{self.file}'

    def __str__(self):
        return f'{self.id} <{self.title}>'


class TwitterFeed(TrackedModel, InfoMixin, IndexingMixin):
    title = models.CharField(default=str, max_length=20, blank=True)
    type = models.CharField(choices=TWITTER_TYPES, max_length=50)
    link = models.URLField(max_length=512, blank=True, null=True)

    table_descriptors = (
        'title',
        'type',
    )

    detail_descriptors = {
        'basic': (
            'title',
            'type',
            'link',
        ),
        'related': (),
    }

    def __str__(self):
        return f'{self.id} <{self.title}>'
