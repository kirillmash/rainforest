from rest_framework import serializers

from .models import Product, Order, ProductsInOrder


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'cost',
            'price',
            'quantity'
        ]
        read_only_fields = ('id', 'title',)


class ProductsInOrderSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=False)

    class Meta:
        model = ProductsInOrder
        fields = [
            'order',
            'product',
            'quantity'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    products = serializers.ListField(child=ProductsInOrderSerializer())

    class Meta:
        model = Order
        fields = [
            'products',
        ]


# class ProductsListInOrderSerializer(serializers.ModelSerializer):
#     product = serializers.SerializerMethodField()
#     quantity = serializers.SerializerMethodField()
#
#     @staticmethod
#     def get_product(instance):
#         return instance.title
#
#     @staticmethod
#     def get_quantity(instance):
#         print(instance)
#         # return instance.products_in_order.get(product=instance).quantity
#         return ''
#
#     class Meta:
#         model = ProductsInOrder
#         fields = [
#             'product',
#             'quantity'
#         ]


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    @staticmethod
    def get_products(instance):
        return [{"title": pr.product.title, "quantity": pr.quantity} for pr in instance.products_in_order.all()]

    class Meta:
        model = Order
        fields = [
            'id',
            'products',
            'created_at',
            'total_price',
            'status',
        ]


class ReportProductsInOrderSerializer(serializers.ModelSerializer):
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    profit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    product__title = serializers.CharField(required=False)
    quantity_sold = serializers.IntegerField(required=False)

    class Meta:
        model = ProductsInOrder
        fields = ('product__title', 'revenue',  'profit', 'quantity_sold')
