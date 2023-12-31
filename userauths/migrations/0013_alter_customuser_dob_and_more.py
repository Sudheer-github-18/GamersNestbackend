# Generated by Django 4.2.5 on 2023-11-28 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0012_alter_customuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='dob',
            field=models.DateField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_otp_attempt',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='otp_expiry',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
