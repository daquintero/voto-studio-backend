from django.conf import settings
from shared.utils import get_model


def get_models_to_index():
    try:
        return settings.MODELS_TO_INDEX
    except AttributeError as e:
        raise AttributeError(f"{e}. Have you added 'MODELS_TO_INDEX' to your settings file?")


def get_fields(model_class=None, model_label=None):
    """
    Get the fields we want to be able to search against.
    """
    _model_class = model_class
    if model_label is not None:
        _model_class = get_model(model_label=model_label)
    # The FileField type includes ImageFields as well.
    fields = [f for f in _model_class._meta.get_fields()
              if not (f.is_relation or f.get_internal_type() == 'FileField')]

    return fields
