from django.core.management.base import BaseCommand

from data.regex import update_rels_dict
from voto_studio_backend.forms.views import get_model


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--model_label', action='store', dest='model_label', help='Model label')
        parser.add_argument('--using', action='store', dest='using', help='The DB to act on')

    def handle(self, *args, **options):
        model_label = options.get('model_label')
        ans = input(f'This will update the rels dict on {model_label}! '
                    f'Do you wish to continue? [y/N] ')
        confirm = ans.lower() == 'y'

        if confirm:
            update_rels_dict(model_class=get_model(model_label=model_label), using=options.get('using'))
            self.stdout.write(f"Successfully updated rels_dict on {model_label}.")
        else:
            self.stdout.write('Cancelled.')
