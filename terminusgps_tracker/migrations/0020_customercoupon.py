# Generated by Django 5.1.9 on 2025-05-14 18:29

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0019_alter_customersubscription_trial_months'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed', models.BooleanField(default=False)),
                ('percent_off', models.PositiveSmallIntegerField(default=15, validators=[django.core.validators.MinValueValidator(15), django.core.validators.MaxValueValidator(100)])),
                ('total_months', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(24)])),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='terminusgps_tracker.customer')),
            ],
        ),
    ]
