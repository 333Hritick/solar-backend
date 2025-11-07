from django.urls import path
from.views import create_quote
from .import views
from .views import register_user, login_user


urlpatterns = [
    path('quote/',create_quote,name='create_quote'),
    path('calculate_emi/', views.calculate_emi, name='calculate_emi'),
    path('register/', register_user),
    path('login/', login_user),
    
]
