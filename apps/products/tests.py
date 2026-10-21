
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Stock


User = get_user_model()


class ProductEditTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='vendedor1',
            email='vendedor1@teste.com',
            password='senha-teste-123',
            user_type='SELLER',
        )
        self.other_seller = User.objects.create_user(
            username='vendedor2',
            email='vendedor2@teste.com',
            password='senha-teste-123',
            user_type='SELLER',
        )

        self.category = Category.objects.create(
            name='Tênis',
            slug='tenis',
        )

        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Tênis antigo',
            description='Descrição antiga',
            brand='Marca A',
            price='100.00',
        )

        self.edit_url = reverse(
            'products:product-edit',
            kwargs={'pk': self.product.pk},
        )
        self.toggle_url = reverse(
            'products:product-toggle-active',
            kwargs={'pk': self.product.pk},
        )
        self.list_url = reverse('products:product-list-seller')

    def login_seller(self):
        self.client.login(
            email='vendedor1@teste.com',
            password='senha-teste-123',
        )

    def test_seller_can_open_own_product_edit_page(self):
        self.login_seller()

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tênis antigo')
        self.assertContains(response, 'Salvar alterações')

    def test_seller_cannot_edit_another_sellers_product(self):
        self.client.login(
            email='vendedor2@teste.com',
            password='senha-teste-123',
        )

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 404)

    def test_seller_can_update_own_product(self):
        self.login_seller()

        data = {
            'name': 'Tênis atualizado',
            'description': 'Nova descrição',
            'brand': 'Marca B',
            'price': '150.00',
            'category': str(self.category.pk),

            'images-TOTAL_FORMS': '3',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '10',

            'stock-TOTAL_FORMS': '1',
            'stock-INITIAL_FORMS': '0',
            'stock-MIN_NUM_FORMS': '0',
            'stock-MAX_NUM_FORMS': '30',
            'stock-0-size': '40',
            'stock-0-quantity': '5',
        }

        response = self.client.post(self.edit_url, data)

        self.assertRedirects(response, self.list_url)

        self.product.refresh_from_db()

        self.assertEqual(self.product.name, 'Tênis atualizado')
        self.assertEqual(self.product.description, 'Nova descrição')
        self.assertEqual(self.product.brand, 'Marca B')
        self.assertEqual(str(self.product.price), '150.00')

        self.assertTrue(
            Stock.objects.filter(
                product=self.product,
                size='40',
                quantity=5,
            ).exists()
        )

    def test_seller_can_deactivate_product_without_deleting_it(self):
        self.login_seller()

        response = self.client.post(self.toggle_url)

        self.product.refresh_from_db()

        self.assertRedirects(response, self.list_url)
        self.assertFalse(self.product.is_active)
        self.assertTrue(
            Product.objects.filter(pk=self.product.pk).exists()
        )

    def test_seller_can_reactivate_product(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])

        self.login_seller()

        response = self.client.post(self.toggle_url)

        self.product.refresh_from_db()

        self.assertRedirects(response, self.list_url)
        self.assertTrue(self.product.is_active)

    def test_unauthenticated_user_cannot_edit_product(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/', response.url)

    def test_toggle_requires_post(self):
        self.login_seller()

        response = self.client.get(self.toggle_url)

        self.assertEqual(response.status_code, 405)
