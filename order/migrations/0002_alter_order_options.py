# Generated by Django 4.2.7 on 2023-12-04 01:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': [('manage_in_assembly_only', 'Can manage an order with `in assembly` process status only'), ('manage_in_delivery_only', 'Can manage an order with `in delivery` process status only')], 'verbose_name': 'order', 'verbose_name_plural': 'orders'},
        ),
    ]
