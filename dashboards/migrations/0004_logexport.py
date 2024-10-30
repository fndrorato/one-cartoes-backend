# Generated by Django 5.1.1 on 2024-10-30 18:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0007_alter_clients_created_by_alter_clients_group_and_more'),
        ('dashboards', '0003_alter_sharedlink_info'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LogExport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.TextField(blank=True, null=True)),
                ('resultado', models.BooleanField(default=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_exported_client', to='clients.clients')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_log_dashboard', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]