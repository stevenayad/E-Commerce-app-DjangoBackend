from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from product.models import Product

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


def _get_or_create_cart(user):
   # _ → boolean (True لو اتعمل جديد / False لو كان موجود)
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

#(Performance Optimization)
def _cart_queryset():
    return Cart.objects.prefetch_related(
        'items__product',
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_add(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if product_id is None or quantity is None:
        return Response(
            {'error': 'product_id and quantity are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response(
            {'error': 'quantity must be a positive integer'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity <= 0:
        return Response(
            {'error': 'quantity must be greater than 0'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = Product.objects.filter(pk=product_id).first()
    if product is None:
        return Response(
            {'error': 'Product does not exist'},
            status=status.HTTP_404_NOT_FOUND,
        )

    with transaction.atomic():
        cart = _get_or_create_cart(request.user)
        #select_for_update() بتعمل lock على الصف في DB
        cart = Cart.objects.select_for_update().get(pk=cart.pk)

        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        new_qty = quantity + (cart_item.quantity if cart_item else 0)

        if product.stock < new_qty:
            return Response(
                {'error': 'Not enough stock for this product'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unit_price = product.price
        if cart_item:
            cart_item.quantity = new_qty
            cart_item.price = unit_price
            cart_item.save(update_fields=['quantity', 'price'])
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                price=unit_price,
            )

    cart = _cart_queryset().get(pk=cart.pk)
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_get(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart = _cart_queryset().get(pk=cart.pk)
    serializer = CartSerializer(cart)
    data = serializer.data
    return Response(
        {
            'items': data['items'],
            'total_price': data['total_price'],
        },
        status=status.HTTP_200_OK,
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cart_update(request, item_id):
    quantity = request.data.get('quantity')
    if quantity is None:
        return Response(
            {'error': 'quantity is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response(
            {'error': 'quantity must be a positive integer'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity <= 0:
        return Response(
            {'error': 'quantity must be greater than 0'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_item = get_object_or_404(
        CartItem.objects.select_related('product', 'cart'),
        pk=item_id,
        cart__user=request.user,
    )

    product = cart_item.product
    if product.stock < quantity:
        return Response(
            {'error': 'Not enough stock for this product'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_item.quantity = quantity
    cart_item.price = product.price
    cart_item.save(update_fields=['quantity', 'price'])

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_remove(request, item_id):
    deleted, _ = CartItem.objects.filter(
        item_id,
        request.user,
    ).delete()
    if not deleted:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_clear(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
