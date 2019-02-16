from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('using', type=str)
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')

    def handle(self, *args, **options):
        using = options.get('using')

        if not options.get('bypass'):
            ans = input(f'This will clear ALL form instances on {using}! Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        if confirm:
            total_objects = 0
            for model_label in settings.WORKSHOP_MODELS:
                model_class = apps.get_model(*model_label.split('.'))
                total_objects += model_class.objects.using(using).count()
                model_class.objects.using(using).all().delete()
            self.stdout.write(f'Deleted {total_objects} instances.')
        else:
            self.stdout.write('Cancelled.')
