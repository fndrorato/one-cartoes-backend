# Generated by Django 5.1.1 on 2024-10-22 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_alter_received_data_pagamento_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='received',
            name='valor_liquido_venda',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
