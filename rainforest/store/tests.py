from rest_framework.test import APITestCase

from .models import Product, Order


class StoreApiTestCase(APITestCase):
    def setUp(self) -> None:
        pass

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

