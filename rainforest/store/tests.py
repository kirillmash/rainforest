import json

from rest_framework.test import APITestCase

from .models import Product, Order, ProductsInOrder
from .serializers import ProductSerializer


class StoreApiTestCase(APITestCase):
    def setUp(self) -> None:
        data = {
            "title": "iphone",
            "cost": "700",
            "price": "1500",
            "quantity": "22"
        }
        self.product = Product.objects.create(**data)
        self.order = Order.objects.create()
        self.pio = ProductsInOrder.objects.create(order=self.order, product=self.product, quantity=2)
        self.order.total_price = self.pio.total_price_by_qty
        self.order.save()

    def test_add_product(self):
        data = {
            "title": "macbook",
            "cost": "1200",
            "price": "2000",
            "quantity": "33"
        }
        response = self.client.post('/api/store/products/', data)
        created_product = Product.objects.get(title="macbook")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(created_product.cost, 1200)
        self.assertEqual(created_product.quantity, 33)

    def test_get_list_of_products(self):
        response = self.client.get('/api/store/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response_product_by_id = self.client.patch(f'/api/store/products/?id={self.product.pk}')
        self.assertEqual(response_product_by_id.status_code, 200)
        serializer = ProductSerializer(self.product)
        self.assertEqual(response_product_by_id.data, serializer.data)

    def test_update_product(self):
        data = {
            "quantity": "50"
        }
        response = self.client.patch(f'/api/store/products/?id={self.product.pk}', data)
        self.assertEqual(response.status_code, 200)
        updated_product = Product.objects.get(title="iphone")
        self.assertEqual(updated_product.quantity, 50)

        bad_response = self.client.patch(f'/api/store/products/?id=1245', data)
        self.assertEqual(bad_response.status_code, 404)
        self.assertEqual(bad_response.data, {'detail': 'Product with id=1245 not found'})

    def test_create_order(self):
        data = json.dumps({
            "products": [{"product": self.product.pk, "quantity": 4}]
        })
        response = self.client.post('/api/store/order/', data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        bad_data = json.dumps({
            "products": [{"product": self.product.pk, "quantity": 1000}]
        })
        response = self.client.post('/api/store/order/', bad_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"detail": "Quantity product less then required"})

    def test_update_order(self):
        data = {
            "status": 4
        }
        response = self.client.patch(f'/api/store/order/?id={self.order.pk}', data)
        updated_order = Order.objects.get(pk=self.order.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_order.status, 4)

