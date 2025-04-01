# Generated by Django 5.1.7 on 2025-04-01 20:23

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
            name='SubscriptionFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('desc', models.CharField(max_length=2048)),
                ('amount', models.IntegerField(blank=True, choices=[(5, '5'), (25, '25'), (150, '150'), (999, '∞')], default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('desc', models.CharField(max_length=1024)),
                ('amount', models.DecimalField(decimal_places=2, default=9.99, max_digits=6)),
                ('features', models.ManyToManyField(related_name='features', to='terminusgps_tracker.subscriptionfeature')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorizenet_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('wialon_user_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('wialon_group_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('wialon_resource_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('wialon_super_user_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wialon_id', models.PositiveIntegerField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='terminusgps_tracker.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerPaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorizenet_id', models.PositiveIntegerField()),
                ('default', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='terminusgps_tracker.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorizenet_id', models.PositiveIntegerField()),
                ('default', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='terminusgps_tracker.customer')),
            ],
            options={
                'verbose_name_plural': 'customer shipping addresses',
            },
        ),
        migrations.CreateModel(
            name='CustomerSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorizenet_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('total_months', models.PositiveIntegerField(choices=[(12, '12 months'), (24, '24 months')], default=12)),
                ('trial_months', models.PositiveIntegerField(choices=[(0, '0 months'), (1, '1 month')], default=0)),
                ('status', models.CharField(choices=[('active', 'Active'), ('canceled', 'Canceled'), ('expired', 'Expired'), ('suspended', 'Suspended'), ('terminated', 'Terminated')], default='suspended', max_length=16)),
                ('address', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='terminusgps_tracker.customershippingaddress')),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='subscription', to='terminusgps_tracker.customer')),
                ('payment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='terminusgps_tracker.customerpaymentmethod')),
                ('tier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='terminusgps_tracker.subscriptiontier')),
            ],
        ),
    ]
