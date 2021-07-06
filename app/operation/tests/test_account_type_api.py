from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import AccountType

from operation.serializers import AccountTypeSerializer

ACCOUNT_TYPE_URL = reverse('operation:accounttype-list')


class PublicAccountTypeApiTests(TestCase):
    """Test the publicly available AccountType API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access endpoint"""
        res = self.client.get(ACCOUNT_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAccountTypeApiTests(TestCase):
    """Test the private AccountType API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_account_type_list(self):
        """Test retrieving a list of account types"""
        AccountType.objects.create(user=self.user, name='Bank Account')
        AccountType.objects.create(user=self.user, name='Investments Account')

        res = self.client.get(ACCOUNT_TYPE_URL)

        account_types = AccountType.objects.all().order_by('name')
        serializer = AccountTypeSerializer(account_types, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_account_types_limited_to_user(self):
        """Test that account types for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'whoami@gmail.com',
            'superpassword'
        )
        AccountType.objects.create(user=user2, name='Bank Account')
        account_type = AccountType.objects.create(
            user=self.user,
            name='Investments Account'
            )

        res = self.client.get(ACCOUNT_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], account_type.name)

    def test_create_account_type_successful(self):
        """Test create a new account type"""
        payload = {'name': 'Bank Account'}
        self.client.post(ACCOUNT_TYPE_URL, payload)

        exists = AccountType.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_account_type_invalid(self):
        """Test creating invalid account type fails"""
        payload = {'name': ''}
        res = self.client.post(ACCOUNT_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_calculate_account_type(self):
        """
        Test creating an account type that is not considered in calculations
        """
        account_type = AccountType.objects.create(
            user=self.user,
            name='Food Voucher Account',
            calculate=False
            )
        res = self.client.get(ACCOUNT_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['calculate'], account_type.calculate)
