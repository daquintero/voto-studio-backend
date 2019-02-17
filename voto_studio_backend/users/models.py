from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from voto_studio_backend.forms.models import InfoMixin
from voto_studio_backend.search.models import IndexingMixin, IndexingManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, both_db=False, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **kwargs)
        user.set_password(password)

        if both_db:
            user.save(using=settings.STUDIO_DB)
            user.save(using=settings.MAIN_SITE_DB)
        else:
            user.save(using=settings.STUDIO_DB)

        return self.model.objects.using(settings.STUDIO_DB).get(id=user.id)

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=settings.STUDIO_DB)

        return user


class User(AbstractBaseUser, PermissionsMixin, InfoMixin, IndexingMixin):
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    name = models.CharField(_('name'), max_length=255)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('data joined'), default=timezone.now)
    profile_picture = models.OneToOneField(
        'media.Image',
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='image_owner',
    )

    objects = UserManager()
    search = IndexingManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    table_descriptors = (
        'name',
        'email',
    )

    detail_descriptors = ()

    search_method_fields = (
        'profile_picture_url',
    )

    def __str__(self):
        return f"{self.name} <{self.email}>"

    def get_profile_picture_url(self):
        default_image_url = 'https://s3.amazonaws.com/votoinformado2019/images/default_profile_picture.jpg'

        return self.profile_picture.image.url if self.profile_picture else default_image_url


class Researcher(User):
    institution = models.CharField(max_length=72, default=str, blank=True)

    def __str__(self):
        return f"(r) {self.name} <{self.email}>"
