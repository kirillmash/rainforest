from django.db.models import Count, Sum, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product, ProductsInOrder, Order
from .serializers import ProductSerializer, OrderSerializer, OrderCreateSerializer, ReportProductsInOrderSerializer


class ProductsAPIVIew(APIView):

    def get(self, request):
        products_id = request.query_params.get('id', None)
        products = Product.objects.all()
        if products_id:
            products = products.filter(id=products_id)

        serializer = ProductSerializer(products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        products_id = request.query_params.get('id', None)
        try:
            product = Product.objects.get(id=products_id)
        except Product.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'detail': f'Product with id={products_id} not found'})
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class OrdersAPIView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        order = Order.objects.create()
        products = []
        for product in serializer.validated_data['products']:
            new_product = ProductsInOrder.objects.create(order=order,
                                                         product=product.get('product'),
                                                         quantity=product.get('quantity', 1))
            products.append(new_product)
            order.total_price += new_product.total_price_by_qty

        order.save()
        serialized = OrderSerializer(order)
        return Response(status=status.HTTP_201_CREATED, data=serialized.data)

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def patch(self, request):
        order_id = request.query_params.get('id', None)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'detail': f'Order with id={order_id} not found'})
        status_order = request.data.get('status', None)
        if status_order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': 'Status is required'})
        order.status = int(status_order)
        order.save()
        return Response(status=status.HTTP_200_OK)


class ConsolidatedReportAPIView(APIView):

    def get(self, request):
        queryset = ProductsInOrder.objects.values('product__title').annotate(count=Count('product')).annotate(
            revenue=Sum('total_price_by_qty'), expenses=Sum('total_cost_by_qty'),
            quantity_sold=Sum('quantity')).annotate(
            profit=F('revenue') - F('expenses')
        )
        ser = ReportProductsInOrderSerializer(queryset, many=True)
        return Response(data=ser.data, status=status.HTTP_200_OK)
