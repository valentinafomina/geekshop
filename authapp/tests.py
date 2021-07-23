from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from authapp.models import ShopUser


class UserManagementTestCase(TestCase):
    username = 'django'
    email = 'django@db.local'
    password = 'geekbrains'
    status_success_code = 200

    new_user_data: {
        'username' : 'django1',
        'first_name': 'django',
        'last_name' : 'django',
        'password1' : 'geekbrains',
        'password2' : 'geekbrains',
        'age' : 33,
        'email' : 'django@gb.local'

    }

    def SetUp(self):
        self.user = ShopUser.objects.create_superuser('django', email=self.email, password=self.password)
        self.client = Client


    def test_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertTrue(response.context['user'].is_anonymous)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/auth/login/')
        self.assertFalse(response.status_code, self.status_code_redirect)

    def test_user_register(self):
        response = self.client.post('/auth/register/', data=self.new_user_data)
        self.assertEqual(response.status_code, self.status_code_redirect)

        new_user = ShopUser.objects.get(username=self.new_user_data['username'])

        activation_url = f'{settings.DOMAIN_NAME}/auth/verify/{new_user.email}/{new_user.activation_key}/'

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, self.status_code_success)

        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)



