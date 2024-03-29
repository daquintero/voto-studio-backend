from django.conf import settings
from django.urls import path
from . import views


app_name = 'forms'
api_v1 = settings.API_URL_V1


urlpatterns = [
    path(
        f'{api_v1}/finder/',
        views.InstanceFinderAPI.as_view(),
        name='finder',
    ),
    path(
        f'{api_v1}/build/',
        views.BuildFormAPI.as_view(),
        name='build',
    ),
    path(
        f'{api_v1}/location_picker/',
        views.LocationPickerAPI.as_view(),
        name='location_picker',
    ),
    path(
        f'{api_v1}/update_basic_fields/',
        views.UpdateBasicFieldsAPI.as_view(),
        name='update_basic_fields',
    ),
    path(
        f'{api_v1}/update_media_field/',
        views.UpdateMediaFieldAPI.as_view(),
        name='update_media_field',
    ),
    path(
        f'{api_v1}/update_media_order/',
        views.UpdateMediaOrderAPI.as_view(),
        name='update_media_order',
    ),
    path(
        f'{api_v1}/update_related_field/',
        views.UpdateRelatedFieldAPI.as_view(),
        name='update_related_field',
    ),
    path(
        f'{api_v1}/list_instances/',
        views.InstanceListAPI.as_view(),
        name='list_instances',
    ),
    path(
        f'{api_v1}/list_related_instances/',
        views.RelatedInstanceListAPI.as_view(),
        name='list_related_instances',
    ),
    path(
        f'{api_v1}/detail/',  # TODO: Reorder
        views.InstanceDetailAPI.as_view(),
        name='detail',
    ),
    path(
        f'{api_v1}/publish_instances/',
        views.PublishInstancesAPI.as_view(),
        name='publish_instances',
    ),
    path(
        f'{api_v1}/delete_instances/',
        views.DeleteInstancesAPI.as_view(),
        name='delete_instances',
    ),
]
