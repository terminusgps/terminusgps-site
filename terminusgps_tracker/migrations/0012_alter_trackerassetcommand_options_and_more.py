# Generated by Django 5.1.4 on 2025-01-02 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0011_alter_trackerprofile_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trackerassetcommand',
            options={'verbose_name': 'command', 'verbose_name_plural': 'commands'},
        ),
        migrations.AddField(
            model_name='trackerasset',
            name='wialon_id',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='trackerasset',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
