# Generated by Django 4.2.11 on 2024-10-29 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_complaint_description_alter_complaint_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaintvote',
            name='vote_type',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No')], default='N', max_length=1),
            preserve_default=False,
        ),
    ]