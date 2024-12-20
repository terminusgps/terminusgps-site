# Generated by Django 5.1.4 on 2024-12-19 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0004_trackerasset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackerasset',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='terminusgps_tracker.trackerprofile'),
        ),
    ]