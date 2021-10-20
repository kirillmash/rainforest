from rest_framework import serializers

from .models import Product, Order, ProductsInOrder, Reports


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
        read_only_fields = ('id',)


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


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = [
            'id',
            'title',
            'file',
            'date',
            'is_ready'
        ]
