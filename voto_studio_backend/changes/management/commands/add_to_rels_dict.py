from django.core.management.base import BaseCommand

from ...utils import add_field_to_rels_dict
from voto_studio_backend.forms.views import get_model


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--model_label', action='store', dest='model_label', help='Model label')
        parser.add_argument('--field_name', action='store', dest='field_name', help='Model label')
        parser.add_argument('--using', action='store', dest='using', help='The DB to act on')
        parser.add_argument('--to_index', action='store', dest='to_index', help='Should ElasticSearch index this?')

    def handle(self, *args, **options):
        model_label = options.get('model_label')
        ans = input(f'This will update the rels dict on {model_label}! '
                    f'Do you wish to continue? [y/N] ')
        confirm = ans.lower() == 'y'

        if options.get('to_index') == 'True':
            to_index = True
        else:
            to_index = False

        if confirm:
            add_new_fields_to_rels_dict(
                model_class=get_model(model_label=model_label),
                using=options.get('using'),
                to_index=to_index,
            )
            self.stdout.write(f"Successfully updated rels_dict on {model_label}.")
        else:
            self.stdout.write('Cancelled.')
