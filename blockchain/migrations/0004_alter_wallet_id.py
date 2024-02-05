# Generated by Django 5.0.1 on 2024-02-03 05:19

import blockchain.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0003_remove_transaction_coupon_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='id',
            field=models.CharField(default=blockchain.models.generate_wallet_address, editable=False, max_length=64, primary_key=True, serialize=False),
        ),
    ]