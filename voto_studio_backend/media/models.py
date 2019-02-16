from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


MEDIA_TYPES = (
    ('images', _('Images')),
    ('videos', _('Videos')),
    ('resources', _('Resources')),
)


class BaseMediaModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    type = models.CharField(_('Media Type'), choices=MEDIA_TYPES, max_length=128, default='images')
    # TODO: date_uploaded or datetime_uploaded?
    date_uploaded = models.DateTimeField(_('Date Uploaded'), default=now)

    class Meta:
        abstract = True

    def delete(self, reduce_order=False, using=None, keep_parents=False):
        if reduce_order:
            fields = [field for field in self._meta.get_fields()
                      if isinstance(field, models.ManyToManyRel)]
            for field in fields:
                instances = getattr(self, f'{field.name}_set').all()
                for instance in instances:
                    print(self.id, self.type)
                    instance.reduce_order(self.id, self.type)

        super().delete(using=None, keep_parents=keep_parents)


class Image(BaseMediaModel):
    title = models.CharField(max_length=2048, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

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


class Video(BaseMediaModel):
    title = models.CharField(default=str, max_length=32, blank=True)
    embed_url = models.URLField(max_length=2048, blank=True)

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


class Resource(BaseMediaModel):
    title = models.CharField(default=str, max_length=32, blank=True)
    brief_description = models.CharField(default=str, max_length=128)
    icon = models.CharField(default=str, max_length=32, blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    link = models.URLField(max_length=2048, blank=True)
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

    def __str__(self):
        return f'{self.id} <{self.title}>'
