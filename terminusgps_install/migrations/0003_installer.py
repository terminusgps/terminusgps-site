# Generated by Django 5.1.8 on 2025-04-14 15:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminusgps_install', '0002_wialonasset'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Installer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wialon_id', models.IntegerField(blank=True, default=None, null=True)),
                ('accounts', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='terminusgps_install.wialonaccount')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
