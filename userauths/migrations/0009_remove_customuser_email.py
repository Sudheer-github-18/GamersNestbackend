# Generated by Django 4.2.5 on 2023-11-26 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0008_alter_userprofile_friends'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='email',
        ),
    ]