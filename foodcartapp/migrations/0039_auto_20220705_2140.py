# Generated by Django 3.2 on 2022-07-05 21:40

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=50, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='name',
            field=models.CharField(db_index=True, max_length=50, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='name',
            field=models.CharField(db_index=True, max_length=50, verbose_name='название'),
        ),
    ]
