import copy
import math

from django.conf import settings

from .models import get_rels_dict_default, Change
from voto_studio_backend.users.models import User


def migrate_rels_dict(model_class, using=settings.STUDIO_DB, to_index=True, logging=False):
    # Get all the tracked instances for a given
    # model class in the specified database.
    instances = model_class.objects \
        .using(using) \
        .filter(tracked=True)

    # Exit early if there are no instances of
    # this type in the specified database.
    if not instances.count():
        if logging:
            print('No instances')
        return

    # For each instance rebuild the relationships dictionary.
    for index, instance in enumerate(instances):
        fields = model_class.objects._get_fields()
        # Leave this iteration early if the rels_dict does not need to change.
        if list(instance.rels_dict.keys()) == [field.name for field in fields]:
            continue

        if logging:
            # Provide some indication to the console of
            # the function's progress
            if not index % math.ceil(instances.count() / 10):
                print(f'{round(index / instances.count() * 100)}%')

        # Start with a deep copy of the instance's relationships dictionary
        # and iterate over each of the model class' fields.
        rels_dict = copy.deepcopy(instance.rels_dict)
        for field in fields:
            if field.name not in rels_dict.keys():
                # If the field name is not already included in the
                # rels_dict then this means it is a new field. So
                # we add a default rels_dict entry for the field.
                rels_dict.update({
                    field.name: get_rels_dict_default(field=field),
                })

        for key in instance.rels_dict.keys():
            if key not in [field.name for field in fields]:
                del rels_dict[key]

        # Update the instance and save it.
        instance.rels_dict = rels_dict
        instance.save(using=using, update_fields=['rels_dict'], to_index=to_index)

        # We need to stage a change, so we fake a request
        # and set the user to the migration bot.
        user = User.objects.get(email='migration@bot.com')
        request = type('Request', (object, ), {})
        request.user = user
        Change.objects.stage_updated(instance, request)

    if logging:
        print('100%')
