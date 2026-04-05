from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart
from product.models import Product

from .models import Order, OrderItem
from .serializer import OrderSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related('user')
        .prefetch_related('orderitems')
    )
    serializer = OrderSerializer(orders, many=True)
    return Response({'orders': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('orderitems'),
        id=pk,
        user=request.user,
    )
    serializer = OrderSerializer(order, many=False)
    return Response({'order': serializer.data})


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    new_status = request.data.get('status')
    if new_status is None or new_status == '':
        return Response(
            {'error': 'status is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order.status = new_status
    order.save(update_fields=['status'])

    serializer = OrderSerializer(order, many=False)
    return Response({'order': serializer.data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):
    with transaction.atomic():
        order = get_object_or_404(Order, pk=pk, user=request.user)
        item_ids = list(
            order.orderitems.exclude(product_id__isnull=True).values_list(
                'product_id', 'quantity'
            )
        )
        for product_id, qty in item_ids:
            Product.objects.filter(pk=product_id).update(stock=F('stock') + qty)
        order.delete()

    return Response({'details': 'order is deleted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    data = request.data
    required_fields = ('city', 'zip_code', 'street', 'phone_no', 'country')
    missing = [f for f in required_fields if not str(data.get(f, '')).strip()]
    if missing:
        return Response(
            {'error': f"Missing or empty fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        try:
            cart = Cart.objects.select_for_update().get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = list(cart.items.select_related('product'))
        if not items:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product_ids = [item.product_id for item in items]
        products = {
            p.id: p
            for p in Product.objects.select_for_update().filter(pk__in=product_ids)
        }

        for item in items:
            product = products.get(item.product_id)
            if product is None:
                return Response(
                    {'error': 'A product in your cart is no longer available'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if product.stock < item.quantity:
                return Response(
                    {'error': f'Not enough stock for {product.name}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        total_amount = sum(
            (item.price * item.quantity for item in items),
            Decimal('0'),
        )

        order = Order.objects.create(
            user=request.user,
            city=data['city'],
            zip_code=data['zip_code'],
            street=data['street'],
            phone_no=data['phone_no'],
            country=data['country'],
            state=str(data.get('state', '') or ''),
            total_amount=total_amount,
        )

        for item in items:
            product = products[item.product_id]
            OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                quantity=item.quantity,
                price=item.price,
            )
            product.stock -= item.quantity
            product.save(update_fields=['stock'])

        cart.items.all().delete()

    order = Order.objects.prefetch_related('orderitems').get(pk=order.pk)
    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)
