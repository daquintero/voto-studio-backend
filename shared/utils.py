from django.apps import apps


def get_model(model_label=None, app_label=None, model_name=None):
    if model_label is not None:
        return apps.get_model(*model_label.split('.'))

    if app_label is not None and model_name is not None:
        return apps.get_model(app_label, model_name)
