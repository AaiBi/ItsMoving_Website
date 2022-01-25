from django.contrib.auth.models import User
from django.db import models


class User_Info(models.Model):
    indicatif = models.CharField(max_length=5, default="")
    phone_number = models.CharField(max_length=50)
    Adresse = models.CharField(max_length=300)
    country = models.CharField(max_length=300)
    activated = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    profil_picture = models.ImageField(upload_to='user/images/profil_image/', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
