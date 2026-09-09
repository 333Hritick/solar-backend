from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ✅ Custom User model (must be at top, only once)
class User(AbstractUser):
    email = models.EmailField(unique=True)

class QuoteRequest(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    district = models.CharField(max_length=50)
    monthlyBill = models.DecimalField(max_digits=10, decimal_places=2)
    rooftopArea = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=100)
    accounttype = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class EnergyOrder(models.Model):
    ORDER_TYPES = (
        ('sell', 'Sell'),
        ('buy', 'Buy'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    amount = models.FloatField()  # kWh
    price = models.FloatField()   # price per unit
    renewable_type = models.CharField(max_length=20, default="Solar")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.order_type} - {self.amount} kWh"

class EnergyToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tokens = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.tokens} Tokens"



class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=64, unique=True)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    capacity_kw = models.FloatField(null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default="active")
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class ProductionData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    production = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.production} kWh"

