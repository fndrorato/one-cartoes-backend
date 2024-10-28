# Generated by Django 5.1.1 on 2024-10-27 22:59

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0007_alter_clients_created_by_alter_clients_group_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_url', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('info', models.TextField()),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_links', to='clients.clients')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_shared_links', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
