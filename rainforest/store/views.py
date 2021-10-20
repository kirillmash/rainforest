from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductSerializer, OrderSerializer, OrderCreateSerializer, ReportSerializer
from .services import get_all_products, get_products_by_pk, create_order_with_products, get_all_orders, get_order_by_pk, \
    update_status_order, add_product
from .models import Product, Order
from .tasks import create_task_report
from .exceptions import ProductsNotEnough


class ProductsAPIVIew(APIView):

    @staticmethod
    def get(request):
        """Get list of products or one product by pk"""
        products_id = request.query_params.get('id', None)
        if products_id:
            product = get_products_by_pk(products_id)
            serializer = ProductSerializer(product)
        else:
            products = get_all_products()
            serializer = ProductSerializer(products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        """Add product"""
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        new_product = add_product(serializer.validated_data)
        serialized = ProductSerializer(new_product)
        return Response(status=status.HTTP_201_CREATED, data=serialized.data)

    @staticmethod
    def patch(request):
        """Update product"""
        products_id = request.query_params.get('id', None)
        try:
            product = get_products_by_pk(products_id)
        except Product.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'detail': f'Product with id={products_id} not found'})
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class OrdersAPIView(APIView):

    @staticmethod
    def post(request):
        """create order with list of products"""
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        try:
            order = create_order_with_products(products=serializer.validated_data['products'])
        except ProductsNotEnough as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "Quantity product less then required"})
        serialized = OrderSerializer(order)
        return Response(status=status.HTTP_201_CREATED, data=serialized.data)

    @staticmethod
    def get(request):
        """Get list of orders"""
        orders = get_all_orders()
        serializer = OrderSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @staticmethod
    def patch(request):
        """Update status of order"""
        order_id = request.query_params.get('id', None)
        try:
            order = get_order_by_pk(order_id)
        except Order.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'detail': f'Order with id={order_id} not found'})
        status_order = request.data.get('status', None)
        if status_order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': 'Status is required'})
        update_status_order(order, int(status_order))
        return Response(status=status.HTTP_200_OK)


class ConsolidatedReportAPIView(APIView):

    @staticmethod
    def post(request):
        """Create report with date range"""
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')
        if not date1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'date1 is required'})
        if not date2:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'date2 is required'})
        create_task_report.delay(date1=date1, date2=date2)
        return Response(status=status.HTTP_200_OK)
