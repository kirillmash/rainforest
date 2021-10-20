from .models import Product, ProductsInOrder, Order
from .exceptions import ProductsNotEnough

from django.db.models import QuerySet
from django.db import connection
from typing import List, Tuple


def get_all_products() -> QuerySet[Product]:
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


def get_all_orders() -> QuerySet[Order]:
    return Order.objects.all()


def get_order_by_pk(order_id: int) -> Order:
    return Order.objects.get(pk=order_id)


def update_status_order(order: Order, status: int) -> Order:
    order.status = status
    order.save()
    return order


def get_data_for_report(date_start: str, date_end: str) -> Tuple[connection.cursor, list[str]]:
    sql = """with operations as (
        select pio.product_id, o.status, o.created_at, 
               coalesce(pio.quantity, 0) as quantity, pio.total_cost_by_qty, pio.total_price_by_qty
        from store_productsinorder pio
        left join store_order o on o.id=pio.order_id
    )
    select p.id as product_id , p.title as product_title,
           coalesce(sold_stats.sold_qty, 0) as sold_qty,
           coalesce(refunds.refund_qty, 0) as refund_qty,
           coalesce(sold_stats.sum_revenue, 0) as sum_revenue,
           coalesce(sold_stats.sum_revenue - sold_stats.sum_cost, 0) as profit
    from store_product p
    left join (
            select operations.product_id,
                   sum(operations.quantity)           as sold_qty,
                   sum(operations.total_price_by_qty) as sum_revenue,
                   sum(operations.total_cost_by_qty)  as sum_cost
            from operations
            where operations.status = 1 and operations.created_at  between  %(date1)s and %(date2)s
            group by operations.product_id) sold_stats on p.id=sold_stats.product_id
    left join (select product_id, sum(quantity) as refund_qty from operations where status=4 and created_at  between
     %(date1)s and %(date2)s group by product_id) refunds
        on refunds.product_id=p.id"""

    cursor = connection.cursor()
    cursor.execute(sql, {'date1': date_start, 'date2': date_end})
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return data, column_names
