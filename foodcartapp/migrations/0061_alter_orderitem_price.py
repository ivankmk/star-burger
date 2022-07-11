# Generated by Django 3.2 on 2022-07-11 20:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_alter_orderitem_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена'),
        ),
    ]
