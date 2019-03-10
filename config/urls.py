from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views import defaults as default_views
from config.admin import history_admin, main_site_admin, spatial_admin

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path('history_admin/', history_admin.urls),
    path('main_site_admin/', main_site_admin.urls),
    path('spatial_admin/', spatial_admin.urls),
    # User management
    path(
        'users/',
        include('voto_studio_backend.users.urls', namespace='users'),
    ),
    path(
      'changes/',
      include('voto_studio_backend.changes.urls', namespace='changes'),
    ),
    path(
        'permissions/',
        include('voto_studio_backend.permissions.urls', namespace='permissions'),
    ),
    path(
        'forms/',
        include('voto_studio_backend.forms.urls', namespace='forms'),
    ),
    path(
        'media/',
        include('voto_studio_backend.media.urls', namespace='media'),
    ),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            '400/',
            default_views.bad_request,
            kwargs={'exception': Exception('Bad Request')},
        ),
        path(
            '403/',
            default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')},
        ),
        path(
            '404/',
            default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')},
        ),
        path('500/', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
