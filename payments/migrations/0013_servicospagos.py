# Generated by Django 5.1.1 on 2024-10-25 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0012_product_type_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicosPagos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacao', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
