from django.test import TestCase
from django.test.client import Client

from mainapp.models import ProductCategory, Product


class TestMainSmokeTest(TestCase):
    status_code_success = 200

    def setUp(self):
        cat_1 = ProductCategory.objects.create(
            name='cat 1'
        )
        for i in range(100):
            Product.object.create(
                category=cat_1,
                name=f'prod {i}'
            )
        self.client = Client

    def get_products_item(self):
        return Product.object.all()

    def test_main_app_urls(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)


    def test_products_urls(self):
        for product_item in self.get_products_item():
            response = self.client.get(f'/products/product/{product_item.pk}/')
            self.assertEqual(response.status_code, self.status_code_success)
