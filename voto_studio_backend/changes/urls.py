from django.urls import path
from . import views

app_name = 'changes'

base_v1 = 'api/v1'

urlpatterns = [
    # GET Endpoints
    path(f'{base_v1}/increment_view_count/', views.increment_view_count, name='increment_view_count'),
]
