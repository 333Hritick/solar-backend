from django.db import models

class QuoteRequest(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    phone=models.CharField(max_length=15)
    district=models.CharField(max_length=50)
    monthlyBill=models.DecimalField(max_digits=10,decimal_places=2)
    rooftopArea=models.DecimalField(max_digits=10,decimal_places=2)
    message=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

   
    
# Create your models here.
