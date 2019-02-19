from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Get Endpoints
    path('api/v1/detail/<str:type>/', views.UserDetailAPI.as_view(), name='detail'),
    path('api/v1/list/', views.UserListAPI.as_view(), name='list'),
    # path('api/v1/statistics/<int:user_id>/', views.UserStatisticsAPI.as_view(), name='statistics'),
    # Auth endpoints
    path('api/v1/register/', views.RegisterUserAPI.as_view(), name='register'),
    path('api/v1/login/', views.LoginUserAPI.as_view(), name='login'),
]
