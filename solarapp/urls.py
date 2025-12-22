from django.urls import path
from.views import create_quote,register_user, login_user,calculate_emi,user_profile, next_day_energy,create_order,get_offers,execute_trade
from . import views



urlpatterns = [
    path('quote/',create_quote,),
    path('calculate_emi/', calculate_emi),
    path('register/', register_user),
    path('login/', login_user),
    path("profile/", user_profile),
    path("energypredict/", next_day_energy),
    path("createorder/",create_order),
    path("offers/", get_offers),
    path("buy/<int:order_id>/", execute_trade),

]
