from django.apps import apps
from django.conf import settings


def get_model(model_label=None, app_label=None, model_name=None):
    if model_label is not None:
        return apps.get_model(*model_label.split('.'))

    if app_label is not None and model_name is not None:
        return apps.get_model(app_label, model_name)


def hidden_fields(fields_tuple=(), defaults=True):
    if not isinstance(fields_tuple, tuple):
        raise ValueError('Provide a tuple of hidden fields.')
    if defaults:
        return settings.BASE_HIDDEN_FIELDS + fields_tuple
    else:
        return fields_tuple


def create_slice(page, size):
    page = int(page)
    size = int(size)

    from_ = page * size
    to = from_ + size

    return from_, to
