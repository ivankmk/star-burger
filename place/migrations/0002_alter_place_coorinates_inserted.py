# Generated by Django 3.2 on 2021-10-24 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='coorinates_inserted',
            field=models.DateTimeField(auto_now=True, verbose_name='дата добавления координат'),
        ),
    ]
