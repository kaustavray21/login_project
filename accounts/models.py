from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    login_count = models.PositiveIntegerField(default = 0)

    def  __str__(self):
        return f"{self.user.username}'s Profile"
