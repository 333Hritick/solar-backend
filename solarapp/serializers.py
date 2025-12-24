from rest_framework import serializers
from.models import QuoteRequest
from.models import Profile
from .models import EnergyOrder

class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=QuoteRequest
        fields = ['name', 'email', 'phone', 'district', 'monthlyBill', 'rooftopArea', 'message']

        model=Profile
        fields = ['user', 'phone', 'address', 'accounttype']

class EnergyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyOrder
        fields = "__all__"