# Generated by Django 4.2.5 on 2023-11-30 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0018_remove_customuser_social_auth_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='social_auth_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
