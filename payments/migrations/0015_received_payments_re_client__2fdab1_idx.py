# Generated by Django 5.1.1 on 2024-11-13 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adquirentes', '0001_initial'),
        ('clients', '0007_alter_clients_created_by_alter_clients_group_and_more'),
        ('payments', '0014_alter_received_divergencias_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='received',
            index=models.Index(fields=['client', 'data_pagamento'], name='payments_re_client__2fdab1_idx'),
        ),
    ]