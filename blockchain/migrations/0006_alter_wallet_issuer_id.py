# Generated by Django 5.0.1 on 2024-02-03 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0005_rename_user_id_wallet_issuer_id_alter_wallet_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='issuer_id',
            field=models.CharField(max_length=50),
        ),
    ]
