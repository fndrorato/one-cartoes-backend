# Generated by Django 5.1.1 on 2024-11-18 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0006_alter_sharedlink_client'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logexport',
            name='client',
        ),
    ]
