from django.conf import settings
from django.core.management.base import BaseCommand
from voto_backend.spatial import models


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

            total_objects += models.GeometryCollection.objects.using(settings.SPATIAL_DB).count()
            models.GeometryCollection.objects.using(settings.SPATIAL_DB).all().delete()

            total_objects += models.Geometry.objects.using(settings.SPATIAL_DB).count()
            models.Geometry.objects.using(settings.SPATIAL_DB).all().delete()

            total_objects += models.DataSet.objects.using(settings.SPATIAL_DB).count()
            models.DataSet.objects.using(settings.SPATIAL_DB).all().delete()

            self.stdout.write(f'Deleted {total_objects} instances.')
        else:
            self.stdout.write('Cancelled.')
