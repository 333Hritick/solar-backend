import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "solar"
email = "hritickkumar3138@2626"
password = "3138hritick@2626"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(" Superuser created successfully!")
else:
    print(" Superuser already exists.")
