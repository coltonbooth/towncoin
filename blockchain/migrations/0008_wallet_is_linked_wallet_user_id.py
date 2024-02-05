# Generated by Django 5.0.1 on 2024-02-04 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0007_remove_transaction_state_transaction_on_chain'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='is_linked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wallet',
            name='user_id',
            field=models.CharField(default='', max_length=50),
        ),
    ]
