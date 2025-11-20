from django.urls import path
from.views import create_quote,register_user, login_user,calculate_emi,user_profile



urlpatterns = [
    path('quote/',create_quote,),
    path('calculate_emi/', calculate_emi),
    path('register/', register_user),
    path('login/', login_user),
    path("profile/", user_profile),    
]
