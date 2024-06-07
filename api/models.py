from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import secrets
import string


class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bearer_token = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'User token for {self.user.username}'


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        alphabet = string.ascii_letters + string.digits
        bearer_token = ''.join(secrets.choice(alphabet) for _ in range(32))
        UserToken.objects.create(user=instance, bearer_token=bearer_token)


class ComplaintType(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)


class City(models.Model):
    name = models.CharField(max_length=64)


class RoadType(models.Model):
    name = models.CharField(max_length=32)


class Complaint(models.Model):
    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.CASCADE)
    description = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    accuracy = models.FloatField()
    photo = models.ImageField(upload_to='complaint_photos/')
    road_type = models.ForeignKey(RoadType, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
