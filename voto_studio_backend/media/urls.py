from django.conf import settings
from django.urls import path
from . import views


app_name = 'media'
api_v1 = settings.API_URL_V1


urlpatterns = [
    path(
        f'{api_v1}/list_files/',
        views.ListFileAPI.as_view(),
        name='list_files',
    ),
    path(
        f'{api_v1}/upload_files/',
        views.UploadFileAPI.as_view(),
        name='upload_files',
    ),
    path(
        f'{api_v1}/update_file/',
        views.UpdateFileAPI.as_view(),
        name='update_file',
    ),
    path(
        f'{api_v1}/delete_files/',
        views.DeleteFilesAPI.as_view(),
        name='delete_files',
    ),
]
