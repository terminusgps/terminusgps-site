# Generated by Django 5.1.5 on 2025-01-29 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0015_remove_trackerasset_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackerasset',
            name='icon',
            field=models.FileField(blank=True, default=None, null=True, upload_to=''),
        ),
    ]
