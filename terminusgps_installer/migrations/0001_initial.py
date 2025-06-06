# Generated by Django 5.1.9 on 2025-05-30 21:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WialonAccount',
            fields=[
                ('id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('uid', models.IntegerField(blank=True, default=None, null=True)),
            ],
            options={
                'verbose_name': 'account',
                'verbose_name_plural': 'accounts',
            },
        ),
        migrations.CreateModel(
            name='WialonAsset',
            fields=[
                ('id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('imei', models.CharField(max_length=19)),
            ],
            options={
                'verbose_name': 'asset',
                'verbose_name_plural': 'assets',
            },
        ),
        migrations.CreateModel(
            name='Installer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('accounts', models.ManyToManyField(blank=True, default=None, related_name='accounts', to='terminusgps_installer.wialonaccount')),
            ],
            options={
                'verbose_name': 'installer',
                'verbose_name_plural': 'installers',
            },
        ),
        migrations.CreateModel(
            name='InstallJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('installer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='terminusgps_installer.installer')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='terminusgps_installer.wialonaccount')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='job', to='terminusgps_installer.wialonasset')),
            ],
            options={
                'verbose_name': 'install job',
                'verbose_name_plural': 'install jobs',
            },
        ),
        migrations.CreateModel(
            name='WialonAssetCommand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cmd_id', models.PositiveBigIntegerField()),
                ('cmd_type', models.CharField(choices=[('block_engine', 'Block Engine'), ('unblock_engine', 'Unblock Engine'), ('custom_msg', 'Custom Message'), ('driver_msg', 'Driver Message'), ('download_msgs', 'Download Messages'), ('query_pos', 'Query Position'), ('query_photo', 'Query Photo'), ('output_on', 'Output On'), ('output_off', 'Output Off'), ('send_pos', 'Send Position'), ('set_report_interval', 'Set Report Interval'), ('upload_cfg', 'Upload Configuration'), ('upload_sw', 'Upload Firmware')], default='custom_msg', max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('message', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commands', to='terminusgps_installer.wialonasset')),
            ],
            options={
                'verbose_name': 'asset command',
                'verbose_name_plural': 'asset commands',
                'unique_together': {('asset', 'cmd_id')},
            },
        ),
    ]
