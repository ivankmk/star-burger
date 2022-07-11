# Generated by Django 3.2 on 2021-10-24 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_rename_order_status_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('ОБРАБОТАН', 'Обработан'), ('НЕ ОБРАБОТАН', 'Не обработан')], default='НЕ ОБРАБОТАН', max_length=255, verbose_name='Статус заказа'),
        ),
    ]
