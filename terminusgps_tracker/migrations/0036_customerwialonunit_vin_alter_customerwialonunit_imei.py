# Generated by Django 5.2.2 on 2025-06-11 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0035_alter_subscription_tier'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerwialonunit',
            name='vin',
            field=models.CharField(blank=True, default=None, max_length=17, null=True),
        ),
        migrations.AlterField(
            model_name='customerwialonunit',
            name='imei',
            field=models.CharField(blank=True, default=None, max_length=19, null=True),
        ),
    ]
