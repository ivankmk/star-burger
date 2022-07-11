from django.db import models

class Place(models.Model):
    address = models.CharField('адрес', max_length=250, unique=True)
    latitude = models.FloatField('широта', null=True)
    longitude = models.FloatField('долгота', null=True)
    coorinates_inserted = models.DateTimeField(
        'дата добавления координат',
        auto_now=True
    )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'

    def __str__(self):
        return self.address
