# Generated by Django 5.2.3 on 2025-06-29 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_otp_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='code',
            field=models.CharField(max_length=9),
        ),
    ]
