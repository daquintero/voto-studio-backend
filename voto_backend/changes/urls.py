from django.urls import path
from . import views

app_name = 'changes'

base_v1 = 'api/v1'

urlpatterns = [
    # Get Endpoints
    path(f'{base_v1}/list/', views.ChangeListAPI.as_view(), name='list_changes'),
    # Creation endpoints
    # Update endpoints
    path(f'{base_v1}/commit/', views.CommitChangeAPI.as_view(), name='commit_changes'),
]
