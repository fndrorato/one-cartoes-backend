# Generated by Django 5.1.1 on 2024-10-14 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_groups_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
