# Generated by Django 4.0.4 on 2022-11-20 20:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_orders_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orders',
            options={'verbose_name_plural': 'Orders'},
        ),
    ]