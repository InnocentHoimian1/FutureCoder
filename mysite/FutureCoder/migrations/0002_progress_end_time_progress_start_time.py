# Generated by Django 4.1.5 on 2023-01-31 14:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('FutureCoder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='progress',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
