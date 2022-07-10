from django.http import JsonResponse
from django.templatetags.static import static
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import phonenumbers


from .models import Product, Order, OrderItem


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


@api_view(['POST'])
def register_order(request):
    order = request.data
    
    try:
        order['products']
    except KeyError:
        content = {
            'products': 'Обязательное поле.'
        }
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    if isinstance(order['products'], list) and len(order['products']) == 0:
        content = {
            'products': 'Этот список не может быть пустым.'
        }
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    elif not order['products']:
        content = {
            'products': 'Это поле не может быть пустым.'
        }
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    elif isinstance(order['products'], str):
        content = {
            'products': 'Ожидался list со значениями, но был получен "str".'
        }
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    
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
    return Response(order)
