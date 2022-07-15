from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, F
import datetime
from place.utils import fetch_coordinates
from geopy import distance


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def calculate_order_price(self):
        return self.annotate(
            total_price=Sum(F('ordered_items__quantity') *
                            F('ordered_items__price'))
        )


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('ОБРАБОТАН', 'Обработан'),
        ('НЕ ОБРАБОТАН', 'Не обработан'),
    )

    ORDER_PAYMENT_METHODS = (
        ('ОНЛАЙН', 'Оплата онлайн'),
        ('НАЛИЧНЫЕ', 'Оплата наличными'),
    )

    firstname = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    lastname = models.CharField(
        max_length=255,
        verbose_name='Фамилия'
    )
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес'
    )
    phonenumber = PhoneNumberField(
        verbose_name='Телефон',
        db_index=True
        )

    status = models.CharField(
        max_length=255,
        choices=ORDER_STATUS_CHOICES,
        default='НЕ ОБРАБОТАН',
        verbose_name='Статус заказа',
        blank=True
    )

    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        blank=True
    )

    registered_at = models.DateTimeField(
        default=datetime.datetime.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        null=True, blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        null=True, blank=True,
        db_index=True
    )

    payment_method = models.CharField(
        max_length=255,
        choices=ORDER_PAYMENT_METHODS,
        verbose_name='Способ оплаты'
    )

    restaraunt = models.ForeignKey(
        Restaurant,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='ресторан'
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} - {self.lastname}"

    def get_available_restaraunts(self, order_items, menu_items):
        order_items_restaurants = [
            menu_items[order_item['product']] for order_item in order_items]
        order_restaurants = set.intersection(
            *[set(order_item_restaurants) for order_item_restaurants in order_items_restaurants])
        return order_restaurants

    def fetch_restaurants_distance(self, menu_items):
        order_items = self.ordered_items.all().values('product')
        order_restaurants = self.get_available_restaraunts(
            order_items, menu_items)
        order_coordinates = fetch_coordinates(self.address)
        if order_coordinates:
            order_restaurants_coordinates = {}
            for order_restaurant in order_restaurants:
                restaurant_distance = self.fetch_distance(
                    order_coordinates, order_restaurant)
                order_restaurants_coordinates[order_restaurant] = round(
                    restaurant_distance, 3)

            return sorted(order_restaurants_coordinates,
                          key=lambda restaurant: restaurant[1])

    @staticmethod
    def fetch_distance(order_coordinates, order_restaurant):
        if not order_coordinates[0]:
            return
        restaurant_coordinates = fetch_coordinates(order_restaurant.address)
        if not restaurant_coordinates[0]:
            return
        restaurant_distance = distance.distance(
            order_coordinates, restaurant_coordinates).km
        return restaurant_distance


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='ordered_items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='ordered_products',
        verbose_name='Товар'
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Количество'
    )

    price = models.DecimalField(
        'Цена',
        max_digits=8,
        null=True,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Содержимое заказа'
