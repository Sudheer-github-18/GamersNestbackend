# Generated by Django 4.2.5 on 2023-12-05 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0029_alter_userprofile_gamer_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gamer_name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
