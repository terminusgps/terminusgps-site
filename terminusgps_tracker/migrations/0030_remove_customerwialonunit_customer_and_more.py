# Generated by Django 5.2.1 on 2025-06-04 21:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0029_subscription_start_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerwialonunit',
            name='customer',
        ),
        migrations.DeleteModel(
            name='CustomerWialonAccount',
        ),
        migrations.DeleteModel(
            name='CustomerWialonUnit',
        ),
    ]
