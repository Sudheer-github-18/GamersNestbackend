# Generated by Django 4.2.5 on 2023-12-02 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0025_customuser_discord_auth_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='discord_auth_code',
            new_name='discord_auth_key',
        ),
    ]