# Generated by Django 5.0.4 on 2024-04-25 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0003_rename_name_user_first_name_user_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]