from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/energy/", consumers.EnergyConsumer.as_asgi()),
]
