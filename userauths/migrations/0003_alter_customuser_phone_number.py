# Generated by Django 4.2.5 on 2023-10-03 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0002_alter_customuser_user_registered_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]