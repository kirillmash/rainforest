from .models import Product, ProductsInOrder, Order, Reports
from .exceptions import ProductsNotEnough

from django.db.models import QuerySet
from typing import List


def get_all_products() -> QuerySet:
    return Product.objects.all()


def add_product(validate_data: dict) -> Product:
    new_product = Product.objects.create(**validate_data)
    return new_product


def get_products_by_pk(product_pk: int) -> Product:
    return Product.objects.get(pk=product_pk)


def create_order_with_products(products: List) -> Order:
    order = Order.objects.create()
    products_in_order = []
    for product in products:
        product_by_pk = product.get('product')
        quantity_product_in_order = product.get('quantity', 1)
        remaining_amount = product_by_pk.quantity - quantity_product_in_order
        if remaining_amount < 0:
            raise ProductsNotEnough
        new_product = ProductsInOrder.objects.create(order=order,
                                                     product=product_by_pk,
                                                     quantity=quantity_product_in_order)
        product_by_pk.quantity = remaining_amount
        product_by_pk.save()
        products_in_order.append(new_product)
        order.total_price += new_product.total_price_by_qty
    order.save()
    return order


def get_all_orders() -> QuerySet:
    return Order.objects.all()


def get_order_by_pk(order_id: int) -> Order:
    return Order.objects.get(pk=order_id)


def update_status_order(order: Order, status: int) -> Order:
    order.status = status
    order.save()
    return order
