# Generated by Django 5.1.8 on 2025-04-09 20:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0016_alter_customer_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customersubscription',
            name='_prev_address',
        ),
        migrations.RemoveField(
            model_name='customersubscription',
            name='_prev_payment',
        ),
        migrations.RemoveField(
            model_name='customersubscription',
            name='_prev_tier',
        ),
    ]
