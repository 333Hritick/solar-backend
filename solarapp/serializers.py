from rest_framework import serializers
from.models import QuoteRequest

class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=QuoteRequest
        fields = ['name', 'email', 'phone', 'district', 'monthlyBill', 'rooftopArea', 'message']