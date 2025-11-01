from django.urls import path
from.views import create_quote
from .import views


urlpatterns = [
    path('quote/',create_quote,name='create_quote'),
    path('calculate_emi/', views.calculate_emi, name='calculate_emi'),
    
]
