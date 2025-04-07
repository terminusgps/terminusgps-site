# Generated by Django 5.1.8 on 2025-04-07 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0009_customersubscription__prev_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='verified',
            new_name='email_verified',
        ),
        migrations.AddField(
            model_name='customer',
            name='email_otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
