from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from time import gmtime, strftime


class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bearer_token = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'User token for {self.user.username}'


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ComplaintType(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class RoadType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


def complaint_directory_path(instance, filename):
    return strftime(f'complaint_photos/%Y/%m/%d/{instance.complaint_type.name}/{filename}')


class Complaint(models.Model):
    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    accuracy = models.FloatField()
    photo = models.ImageField(upload_to=complaint_directory_path, null=True, blank=True)
    road_type = models.ForeignKey(RoadType, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Complaint {self.complaint_type.name}'
