from rest_framework import serializers
from .models import QuoteRequest, Profile, EnergyOrder


class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = [
            'name',
            'email',
            'phone',
            'district',
            'monthlyBill',
            'rooftopArea',
            'message'
        ]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'accounttype']


class EnergyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyOrder
        fields = "__all__"
