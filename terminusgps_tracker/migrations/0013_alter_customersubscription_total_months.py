# Generated by Django 5.1.8 on 2025-04-09 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_tracker', '0012_customerasset_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersubscription',
            name='total_months',
            field=models.PositiveIntegerField(choices=[(12, '1 year'), (24, '2 years'), (9999, '∞')], default=9999),
        ),
    ]
