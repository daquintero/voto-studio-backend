from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.exceptions import PermissionDenied


def permission_denied_message(obj, instance=None, instances=None):
    instance_obj = {}
    if instance is not None:
        instance_obj = {
            'id': instance.id,
            'model_label': instance._meta.model._meta.label,
        }
    if instances is not None and len(instances):
        instance_obj = {
            'ids': [instance.id for instance in instances],
            'model_label': instances[0]._meta.model._meta.label,
        }

    return {
        **obj,
        **instance_obj,
        'permitted': False,

    }


def get_object_or_403(model_class, operation_tuple, **kwargs):
    instance = get_object_or_404(model_class, **kwargs)
    user, operation = operation_tuple
    if instance.is_permitted(user, operation):
        return instance
    else:
        raise PermissionDenied(permission_denied_message({
            'message': f'You do not have {operation} permission on this content.',
        }, instance=instance))


def get_list_or_403(model_class, operation_tuple, **kwargs):
    instances = get_list_or_404(model_class, **kwargs)
    user, operation = operation_tuple
    for instance in instances:
        if not instance.is_permitted(user, operation_tuple):
            raise PermissionDenied(permission_denied_message({
                'message': f'You do not have {operation} permission on all of this content.',
            }, instances=instances))

    return instances
