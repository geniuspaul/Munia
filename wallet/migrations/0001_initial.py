# Generated by Django 5.2.3 on 2025-06-30 11:34

import django.db.models.deletion
import wallet.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.UUIDField(auto_created=True, editable=False, primary_key=True, serialize=False)),
                ('wallet_address', models.CharField(default=wallet.models.generate_wallet_address, max_length=255, unique=True)),
                ('balance', models.DecimalField(decimal_places=8, default=0, max_digits=18)),
                ('currency', models.CharField(default='USD', max_length=10)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
