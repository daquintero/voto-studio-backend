from django.conf import settings
from shared.utils import get_model


def get_models_to_index():
    try:
        return settings.MODELS_TO_INDEX
    except AttributeError as e:
        raise AttributeError(f"{e}. Have you added 'MODELS_TO_INDEX' to your settings file?")


def get_fields(model_label):
    """
    Get the fields we want to be able to search against.
    """
    model_class = get_model(model_label)
    # The FileField type includes ImageFields as well.
    fields = [f for f in model_class._meta.get_fields()
              if not (f.is_relation or f.get_internal_type() == 'FileField')]

    return fields
