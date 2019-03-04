from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('using', type=str)
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')
        parser.add_argument('--user', action='store', dest='user', help='Clear instances for only this user')

    def handle(self, *args, **options):
        using = options.get('using')
        user = options.get('user')

        filter_kwargs = {}
        if not user == 'all':
            user = get_user_model().objects.get(email=user)
            filter_kwargs.update({'user': user})

        if not options.get('bypass'):
            ans = input(f'This will clear ALL form instances on {using}! Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        if confirm:
            total_objects = 0
            for model_label in settings.WORKSHOP_MODELS:
                model_class = apps.get_model(*model_label.split('.'))
                instances = model_class.objects.using(using).filter(**filter_kwargs)
                total_objects += instances.count()
                instances.delete()
            self.stdout.write(f'Deleted {total_objects} instances.')
        else:
            self.stdout.write('Cancelled.')
