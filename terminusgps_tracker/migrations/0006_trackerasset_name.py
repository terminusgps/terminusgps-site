# Generated by Django 5.1.4 on 2024-12-19 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0005_alter_trackerasset_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackerasset',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=64, null=True),
        ),
    ]
