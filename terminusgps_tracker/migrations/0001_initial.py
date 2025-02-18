# Generated by Django 5.1.5 on 2025-02-18 20:10

import django.db.models.deletion
import terminusgps_tracker.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackerSubscriptionFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('desc', models.TextField(blank=True, default=None, max_length=2048, null=True)),
            ],
            options={
                'verbose_name': 'subscription feature',
                'verbose_name_plural': 'subscription features',
            },
        ),
        migrations.CreateModel(
            name='TrackerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorizenet_id', models.PositiveBigIntegerField(blank=True, default=None, null=True)),
                ('wialon_group_id', models.PositiveBigIntegerField(blank=True, default=None, null=True, validators=[terminusgps_tracker.validators.validate_wialon_unit_group_id])),
                ('wialon_resource_id', models.PositiveBigIntegerField(blank=True, default=None, null=True, validators=[terminusgps_tracker.validators.validate_wialon_resource_id])),
                ('wialon_end_user_id', models.PositiveBigIntegerField(blank=True, default=None, null=True, validators=[terminusgps_tracker.validators.validate_wialon_user_id])),
                ('wialon_super_user_id', models.PositiveBigIntegerField(blank=True, default=None, null=True, validators=[terminusgps_tracker.validators.validate_wialon_user_id])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'profile',
                'verbose_name_plural': 'profiles',
            },
        ),
        migrations.CreateModel(
            name='TrackerPaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default', models.BooleanField(default=False)),
                ('authorizenet_id', models.PositiveBigIntegerField(blank=True, default=None, null=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='terminusgps_tracker.trackerprofile')),
            ],
            options={
                'verbose_name': 'payment method',
                'verbose_name_plural': 'payment methods',
            },
        ),
        migrations.CreateModel(
            name='TrackerAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wialon_id', models.CharField(max_length=8, validators=[terminusgps_tracker.validators.validate_wialon_unit_id])),
                ('name', models.CharField(blank=True, default=None, max_length=64, null=True, validators=[terminusgps_tracker.validators.validate_wialon_unit_name_unique])),
                ('hw_type', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('phone_number', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('imei_number', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('is_active', models.BooleanField(blank=True, default=None, null=True)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='terminusgps_tracker.trackerprofile')),
            ],
            options={
                'verbose_name': 'asset',
                'verbose_name_plural': 'assets',
            },
        ),
        migrations.CreateModel(
            name='TrackerShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default', models.BooleanField(default=False)),
                ('authorizenet_id', models.PositiveBigIntegerField(blank=True, default=None, null=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='terminusgps_tracker.trackerprofile')),
            ],
            options={
                'verbose_name': 'shipping address',
                'verbose_name_plural': 'shipping addresses',
            },
        ),
        migrations.CreateModel(
            name='TrackerSubscriptionTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('wialon_id', models.PositiveBigIntegerField(blank=True, default=None, null=True)),
                ('wialon_cmd', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=14)),
                ('period', models.PositiveSmallIntegerField(choices=[(1, 'Monthly'), (3, 'Quarterly'), (12, 'Annually')], default=1)),
                ('length', models.PositiveSmallIntegerField(choices=[(6, 'Half Year'), (12, 'Full Year')], default=12)),
                ('features', models.ManyToManyField(to='terminusgps_tracker.trackersubscriptionfeature')),
            ],
            options={
                'verbose_name': 'subscription tier',
                'verbose_name_plural': 'subscription tiers',
            },
        ),
        migrations.CreateModel(
            name='TrackerSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorizenet_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('payment_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('address_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('suspended', 'Suspended'), ('canceled', 'Canceled'), ('terminated', 'Terminated')], default='suspended', max_length=10)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='terminusgps_tracker.trackerprofile')),
                ('tier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tier', to='terminusgps_tracker.trackersubscriptiontier')),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions',
            },
        ),
    ]
