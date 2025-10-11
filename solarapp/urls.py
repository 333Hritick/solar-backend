from django.urls import path
from.views import create_quote
from .views import home


urlpatterns = [
    path('quote/',create_quote,name='create_quote'),
     path('', home),  
]
