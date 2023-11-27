# Generated by Django 4.2.5 on 2023-10-10 12:49

import django.core.validators
from django.db import migrations, models
import userauths.models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0004_rename_first_name_userprofile_full_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, default='default.jpg', null=True, upload_to=userauths.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default='', max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 digits only.', regex='^\\d{10}')]),
        ),
    ]