# Generated by Django 5.2.2 on 2025-06-13 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0037_alter_subscription_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerwialonunit',
            name='tier',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='terminusgps_tracker.subscriptiontier'),
            preserve_default=False,
        ),
    ]
