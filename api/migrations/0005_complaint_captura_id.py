# Generated by Django 4.2.11 on 2024-11-03 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_complaintvote_vote_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='captura_id',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]