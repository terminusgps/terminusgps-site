# Generated by Django 5.1.8 on 2025-04-09 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0013_alter_customersubscription_total_months'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': [('add_customer_asset', 'Can add a customer asset')]},
        ),
    ]
