# Generated by Django 4.2.5 on 2023-11-30 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0015_alter_userprofile_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='social_auth_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
