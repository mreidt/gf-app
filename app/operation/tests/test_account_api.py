from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Account, AccountType

from operation.serializers import AccountSerializer, AccountDetailSerializer

ACCOUNT_URL = reverse('operation:account-list')


def detail_url(account_id):
    """Return account detail URL"""
    return reverse('operation:account-detail', args=[account_id])


def sample_account_type(user, name='Sample Account Type', calculate=True):
    """Create and return a sample account type"""
    return AccountType.objects.create(
        user=user,
        name=name,
        calculate=calculate
        )


def sample_account(user, **params):
    """Create and return a sample account"""
    defaults = {
        'name': 'Sample Account'
    }
    defaults.update(params)

    return Account.objects.create(user=user, **defaults)


class PublicAccountApiTests(TestCase):
    """Test the publicly available Account API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access endpoint"""
        res = self.client.get(ACCOUNT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAccountApiTests(TestCase):
    """Test the private Account API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_account_list(self):
        """Test retrieving a list of accounts"""
        sample_account(user=self.user)
        sample_account(user=self.user)

        res = self.client.get(ACCOUNT_URL)

        accounts = Account.objects.all().order_by('id')
        serializer = AccountSerializer(accounts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_accounts_limited_to_user(self):
        """Test retrieving accounts for user"""
        user2 = get_user_model().objects.create_user(
            'doctorWho@gmail.com',
            'pass123'
        )
        sample_account(user=user2)
        sample_account(user=self.user)

        res = self.client.get(ACCOUNT_URL)

        accounts = Account.objects.filter(user=self.user)
        serializer = AccountSerializer(accounts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_account_detail(self):
        """Test viewing a account detail"""
        new_acctype = AccountType.objects.create(
                user=self.user,
                name='Test Account Type'
            )
        account = sample_account(user=self.user, acctype=new_acctype)

        url = detail_url(account.id)
        res = self.client.get(url)

        serializer = AccountDetailSerializer(account)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_account(self):
        """Test creating account"""
        new_acctype = AccountType.objects.create(
                user=self.user,
                name='Test Account Type'
            )
        payload = {
            'name': 'National Bank Account',
            'acctype': new_acctype.id
        }
        res = self.client.post(ACCOUNT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        account = Account.objects.get(id=res.data['id'])
        self.assertEqual(payload.get("name"), account.name)
        self.assertEqual(payload.get("acctype"), account.acctype.id)

    def test_create_inactive_account(self):
        """Test creating an inactive account"""
        new_acctype = AccountType.objects.create(
                user=self.user,
                name='Test Account Type'
            )
        payload = {
            'name': 'National Bank Account',
            'acctype': new_acctype.id,
            'active': False,
        }
        res = self.client.post(ACCOUNT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        account = Account.objects.get(id=res.data['id'])
        self.assertEqual(payload.get("name"), account.name)
        self.assertEqual(payload.get("active"), account.active)
        self.assertEqual(payload.get("acctype"), account.acctype.id)

    def test_partial_update_account(self):
        """Test updating a account with patch"""
        new_acctype = AccountType.objects.create(
                user=self.user,
                name='Test Account Type'
            )
        account = sample_account(user=self.user, acctype=new_acctype)

        payload = {'name': 'Universal Bank'}
        url = detail_url(account.id)
        self.client.patch(url, payload)

        account.refresh_from_db()
        self.assertEqual(account.name, payload['name'])

    def test_full_update_account(self):
        """Test updating a account with put"""
        new_acctype = AccountType.objects.create(
                user=self.user,
                name='Test Account Type'
            )
        account = sample_account(user=self.user, acctype=new_acctype)
        new_account_type = sample_account_type(
            user=self.user,
            name='New Account Type'
            )
        payload = {
            'name': 'New Name Account',
            'acctype': new_account_type.id,
            'active': False
        }
        url = detail_url(account.id)
        self.client.put(url, payload)

        account.refresh_from_db()
        self.assertEqual(account.name, payload['name'])
        self.assertEqual(account.active, payload['active'])
        account_type = account.acctype
        self.assertEqual(new_account_type, account_type)
