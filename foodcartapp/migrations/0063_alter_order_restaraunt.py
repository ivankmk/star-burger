# Generated by Django 3.2 on 2022-07-11 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0062_alter_order_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='restaraunt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
    ]
