from django.conf import settings
from django.urls import path
from . import views


app_name = 'forms'
api_v1 = settings.API_URL_V1


urlpatterns = [
    path(
        f'{api_v1}/list/',
        views.ModelListAPI.as_view(),
        name='list',
    ),
    path(
        f'{api_v1}/build/',
        views.BuildFormAPI.as_view(),
        name='build',
    ),
    path(
        f'{api_v1}/related_fields/',  # TODO: Rename to /get_related_fields/ ??
        views.RelatedFieldsAPI.as_view(),
        name='related_fields',
    ),
    path(
        f'{api_v1}/detail/',  # TODO: Reorder
        views.InstanceDetailAPI.as_view(),
        name='detail',
    ),
    path(
        f'{api_v1}/update_basic_fields/',
        views.UpdateBasicFieldsAPI.as_view(),
        name='update_basic_fields',
    ),
    path(
        f'{api_v1}/update_related_fields/',
        views.UpdateRelatedFieldAPI.as_view(),
        name='update_related_fields',
    ),
    path(
        f'{api_v1}/publish/',
        views.PublishContentAPI.as_view(),
        name='publish',
    ),
    path(
        f'{api_v1}/delete_instance/',
        views.DeleteInstanceAPI.as_view(),
        name='delete_instance',
    ),
]
