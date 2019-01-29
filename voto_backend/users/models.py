from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


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


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    name = models.CharField(_('name'), max_length=255)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('data joined'), default=timezone.now)
    profile_picture = models.OneToOneField(
        'content.Image',
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='image_owner'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Researcher(User):
    institution = models.CharField(max_length=72, default=str, blank=True)

    def __str__(self):
        return f"(r) {self.name} <{self.email}>"