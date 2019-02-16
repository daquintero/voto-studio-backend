from django.conf import settings
from django.shortcuts import get_object_or_404
from functools import wraps
from rest_framework.authtoken.models import Token
from .test_app.models import BasicModel
from voto_studio_backend.users.models import User


def get_field(field_name, fields):
    return list(filter(lambda f: f.name == field_name, fields))[0]


def auth_header(user):
    token, _ = Token.objects.get_or_create(user=user)
    return f'Token {token}'


def create_test_user(test_method):
    @wraps(test_method)
    def wrapper(*args):
        user = User.objects.create_user(
            email='foobaz@bar.com',
            name='Baz',
            password='Foobarbaz123',
            both_db=True,
        )
        try:
            test_method(args[0], user)

            user_id = user.id
            get_object_or_404(User.objects.using(settings.STUDIO_DB), id=user_id).delete()
            get_object_or_404(User.objects.using(settings.MAIN_SITE_DB), id=user_id).delete()

        except Exception as e:
            user_id = user.id
            get_object_or_404(User.objects.using(settings.STUDIO_DB), id=user_id).delete()
            get_object_or_404(User.objects.using(settings.MAIN_SITE_DB), id=user_id).delete()

            raise e

    return wrapper


def create_instance(**kwargs):
    instance = BasicModel.objects.db_manager(using=settings.STUDIO_DB).create_with_defaults(user=kwargs.get('user'))

    return instance
