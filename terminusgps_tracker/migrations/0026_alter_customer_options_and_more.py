# Generated by Django 5.2.1 on 2025-06-03 18:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0025_subscription_delete_customersubscription'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'customer', 'verbose_name_plural': 'customers'},
        ),
        migrations.AlterModelOptions(
            name='customerpaymentmethod',
            options={'verbose_name': 'customer payment method', 'verbose_name_plural': 'customer payment methods'},
        ),
        migrations.AlterModelOptions(
            name='customershippingaddress',
            options={'verbose_name': 'customer shipping address', 'verbose_name_plural': 'customer shipping addresses'},
        ),
        migrations.AlterModelOptions(
            name='customerwialonaccount',
            options={'verbose_name': 'customer wialon account', 'verbose_name_plural': 'customer wialon accounts'},
        ),
        migrations.AlterModelOptions(
            name='customerwialonunit',
            options={'verbose_name': 'customer wialon unit', 'verbose_name_plural': 'customer wialon units'},
        ),
        migrations.AddField(
            model_name='subscription',
            name='address',
            field=models.OneToOneField(default=523313620, on_delete=django.db.models.deletion.CASCADE, to='terminusgps_tracker.customershippingaddress'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='payment',
            field=models.OneToOneField(default=535741135, on_delete=django.db.models.deletion.CASCADE, to='terminusgps_tracker.customerpaymentmethod'),
            preserve_default=False,
        ),
    ]
