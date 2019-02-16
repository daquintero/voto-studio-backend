import voto_studio_backend.forms.routing

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            voto_studio_backend.forms.routing.websocket_urlpatterns,
        ),
    ),
})
