from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Get endpoints
    path('api/v1/get_user_permissions/', views.GetUserPermissions.as_view(), name='get_user_permissions'),
    # Post endpoints
    path('api/v1/update_user_permission/', views.UpdateUserPermission.as_view(), name='update_user_permission'),
]
