from django.urls import path
from.views import create_quote


urlpatterns = [
    path('quote/',create_quote,name='create_quote'),
]
