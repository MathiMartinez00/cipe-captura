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


class Form(models.Model):
    name = models.CharField(max_length=120)
    version = models.CharField(max_length=5)


class FormFieldType(models.Model):
    name = models.CharField(max_length=120)


class FormField(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    field_type = models.ForeignKey(FormFieldType, on_delete=models.DO_NOTHING)


class FormResponseHeader(models.Model):
    form = models.ForeignKey(Form, on_delete=models.DO_NOTHING)


class FormResponseDetail(models.Model):
    form_response = models.ForeignKey(FormResponseHeader, on_delete=models.DO_NOTHING)
    form_field = models.ForeignKey(FormField, on_delete=models.DO_NOTHING)
    value = models.TextField()

# Preguntas:
# Me tengo que preocupar por la validacion? Si dejare que carguen respuestas por aca deberia,
# pero agrega complejidad ya que debe coincidir con captura
# Porque no uso nomas las tablas de Captura?