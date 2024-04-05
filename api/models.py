from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import secrets
import string


# TODO: Add a way to create users in the website.
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
