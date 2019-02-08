from django.conf import settings
from django.urls import path
from . import views


app_name = 'media'
api_v1 = settings.API_URL_V1


urlpatterns = [
    path(
        f'{api_v1}/list_images/',
        views.ListImageAPI.as_view(),
        name='list_images',
    ),
    path(
        f'{api_v1}/upload_images/',
        views.UploadImageAPI.as_view(),
        name='upload_images',
    ),
    path(
        f'{api_v1}/update_image/',
        views.UpdateImageAPI.as_view(),
        name='update_image',
    ),
    path(
        f'{api_v1}/delete_images/',
        views.DeleteImageAPI.as_view(),
        name='delete_images',
    ),
]
