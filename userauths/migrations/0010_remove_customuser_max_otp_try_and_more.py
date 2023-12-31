# Generated by Django 4.2.5 on 2023-11-27 12:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0009_remove_customuser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='max_otp_try',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='otp_max_out',
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_otp_attempt',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='otp_attempts',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=15, unique=True, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 digits only.', regex='^\\+91?\\d{10}$')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default='', max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be 10 digits only.', regex='^\\+91?\\d{10}$')]),
        ),
    ]
