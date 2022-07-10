from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError

from .models import Product, Order, OrderItem


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True, allow_empty=False
    )

    class Meta:
        model = Order
        fields = [
            'firstname', 'lastname',
            'address', 'phonenumber',
            'products',
        ]


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate(order):
    errors = []
    empty_keys = []

    for key in order.keys():
        if order[key] is None or order[key] == "":
            empty_keys.append(key)
    if empty_keys:
        errors.append(
            {', '.join(empty_keys): 'Это поле не может быть пустым.'})

    if isinstance(order['firstname'], list):
        errors.append({'firstname': ' Not a valid string.'})

    if isinstance(order['products'], list) and len(order['products']) == 0:
        errors.append({'products': 'Этот список не может быть пустым.'})

    if isinstance(order['products'], str):
        errors.append(
            {'products': 'Ожидался list со значениями, но был получен "str".'})

    for ordered_product in order['products']:
        if not Product.objects.filter(id=ordered_product['product']):
            errors.append({
                'products': f'Недопустимый продукт {ordered_product["product"]}'
            })

    if not carrier._is_mobile(
        number_type(phonenumbers.parse(order['phonenumber']))
    ):
        errors.append({'phonenumber': 'Введен некорректный номер телефона.'})

    if errors:
        raise ValidationError(errors)


@api_view(['POST'])
def register_order(request):

    order = request.data
    serializer = OrderSerializer(data=order)
    serializer.is_valid(raise_exception=True)

    customer = Order.objects.create(
        firstname=order['firstname'],
        lastname=order['lastname'],
        address=order['address'],
        phonenumber=order['phonenumber']
    )

    for product in order['products']:
        OrderItem.objects.create(
            customer=customer,
            product=Product.objects.get(id=product['product']),
            quantity=product['quantity']
        )

    return Response(serializer.data)
