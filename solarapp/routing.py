from django.urls import re_path
from . import consumers  # this will refer to solarapp/consumers.py

websocket_urlpatterns = [
    re_path(r'ws/energy/$', consumers.EnergyConsumer.as_asgi()),
]
