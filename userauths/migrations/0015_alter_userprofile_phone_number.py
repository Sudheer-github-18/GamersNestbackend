# Generated by Django 4.2.5 on 2023-11-28 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0014_alter_customuser_otp_expiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
    ]
