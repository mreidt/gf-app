from decimal import Decimal
from core.models import Account, Tag, Operation
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from datetime import datetime, date
from operation.serializers import (OperationSerializer,
                                   OperationDetailSerializer
                                   )

from rest_framework import status
from rest_framework.test import APIClient

import random


OPERATIONS_URL = reverse('operation:operation-list')


def detail_url(operation_id):
    """Return operation detail URL"""
    return reverse('operation:operation-detail', args=[operation_id])


def account_balance_url(account_id):
    """Return account_balance URL"""
    return reverse('operation:operation-account-balance', args=[account_id])


def sample_tag(user, name='Sample tag'):
    """Create an return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_account(user, **params):
    """Create and return a sample account"""
    defaults = {
        'name': 'Sample Account'
    }
    defaults.update(params)

    return Account.objects.create(user=user, **defaults)


def sample_operation(user, **params):
    """Create and return a sample operation"""
    defaults = {
        'name': 'Supermarket',
        'value': -5.00,
        'date': datetime.now().date(),
        'account': sample_account(user)
    }
    defaults.update(params)

    return Operation.objects.create(user=user, **defaults)


class PublicOperationApiTests(TestCase):
    """Test unauthenticated operation API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(OPERATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOperationApiTests(TestCase):
    """Test authenticated operation API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'sample_user@gmail.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_operations(self):
        """Test retrieving a list of operations"""
        sample_operation(user=self.user)
        sample_operation(user=self.user, name='Another operation')

        res = self.client.get(OPERATIONS_URL)

        operations = Operation.objects.all().order_by('-id')
        serializer = OperationSerializer(operations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_operation_limited_to_user(self):
        """Test retrieving operations for user"""
        user2 = get_user_model().objects.create_user(
            'doctorWho@gmail.com',
            'pass123'
        )
        sample_operation(user=user2)
        sample_operation(user=self.user, name='Electronic Shop', value=-75.00)

        res = self.client.get(OPERATIONS_URL)

        operations = Operation.objects.filter(user=self.user)
        serializer = OperationSerializer(operations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_operation_detail(self):
        """Test viewing a operation detail"""
        operation = sample_operation(
            user=self.user,
            account=sample_account(user=self.user)
        )
        operation.tags.add(sample_tag(user=self.user))

        url = detail_url(operation.id)
        res = self.client.get(url)

        serializer = OperationDetailSerializer(operation)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_operation(self):
        """Test creating operation"""
        payload = {
            'name': 'Supermarket',
            'value': -5.00,
            'date': datetime.now().date(),
            'account': sample_account(self.user).id
        }
        res = self.client.post(OPERATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        operation = Operation.objects.get(id=res.data['id'])

        for key in payload.keys():
            if key == 'account':
                self.assertEqual(payload[key], getattr(operation, key).id)
            else:
                self.assertEqual(payload[key], getattr(operation, key))

    def test_create_operation_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Supermarket')
        tag2 = sample_tag(user=self.user, name='Cleaning products')
        payload = {
            'name': 'Supermarket',
            'value': -5.00,
            'date': datetime.now().date(),
            'account': sample_account(self.user).id,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(OPERATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        operation = Operation.objects.get(id=res.data['id'])
        tags = operation.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_partial_update_operation(self):
        """Test updating a operation with patch"""
        operation = sample_operation(user=self.user)
        operation.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Another tag')

        payload = {'name': 'Another operation', 'tags': [new_tag.id]}
        url = detail_url(operation.id)
        self.client.patch(url, payload)

        operation.refresh_from_db()
        self.assertEqual(operation.name, payload['name'])
        tags = operation.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_operation(self):
        """Test updating a operation with put"""
        operation = sample_operation(user=self.user)
        operation.tags.add(sample_tag(user=self.user))
        payload = {
            'name': 'Supermarket',
            'value': -5.00,
            'date': datetime.now().date(),
            'account': sample_account(self.user).id,
        }
        url = detail_url(operation.id)
        self.client.put(url, payload)

        operation.refresh_from_db()
        for key in payload.keys():
            if key == 'account':
                self.assertEqual(payload[key], getattr(operation, key).id)
            else:
                self.assertEqual(payload[key], getattr(operation, key))

        tags = operation.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_operations_by_tags(self):
        """Test returning operations with specific tags"""
        operation1 = sample_operation(
            user=self.user,
            name='Operation 1',
            value=-17.90,
            account=sample_account(user=self.user, name='New account')
        )
        operation2 = sample_operation(
            user=self.user,
            name='Operation 2',
            value=-23.00,
            account=sample_account(user=self.user, name='New account 2')
        )
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')

        operation1.tags.add(tag1)
        operation2.tags.add(tag2)

        operation3 = sample_operation(user=self.user, name='Operation 3')

        res = self.client.get(
            OPERATIONS_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = OperationSerializer(operation1)
        serializer2 = OperationSerializer(operation2)
        serializer3 = OperationSerializer(operation3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_operations_by_account(self):
        """Test returning operations with specific account"""
        account1 = sample_account(user=self.user, name='account 1')
        account2 = sample_account(user=self.user, name='account 2')
        account3 = sample_account(user=self.user, name='account 3')
        operation1 = sample_operation(
            user=self.user,
            name='Operation 1',
            value=-17.90,
            account=account1
        )
        operation2 = sample_operation(
            user=self.user,
            name='Operation 2',
            value=-23.00,
            account=account2
        )

        operation3 = sample_operation(
            user=self.user,
            name='Operation 3',
            account=account3
        )

        res = self.client.get(
            OPERATIONS_URL,
            {'account': f'{account1.id},{account2.id}'}
        )

        serializer1 = OperationSerializer(operation1)
        serializer2 = OperationSerializer(operation2)
        serializer3 = OperationSerializer(operation3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class OperationDateTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'sample_user@gmail.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)
        self.operation = sample_operation(user=self.user)

    def test_filter_operation_by_year(self):
        """Test filtering operation by year"""
        operation1 = sample_operation(user=self.user)
        operation2 = sample_operation(
            user=self.user,
            date=date(datetime.now().year-1, 1, 1)
        )
        operation3 = sample_operation(
            user=self.user,
            date=date(datetime.now().year-2, 1, 1)
        )
        res = self.client.get(
            OPERATIONS_URL,
            {'year': operation2.date.year}
        )

        serializer1 = OperationSerializer(operation1)
        serializer2 = OperationSerializer(operation2)
        serializer3 = OperationSerializer(operation3)

        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_operation_by_year_and_month(self):
        """Test filtering operation by year and month"""
        operation1 = sample_operation(
            user=self.user,
            date=date(year=datetime.now().year, month=1, day=1)
        )
        operation2 = sample_operation(
            user=self.user,
            date=date(year=datetime.now().year-1, month=1, day=1)
        )
        operation3 = sample_operation(
            user=self.user,
            date=date(year=datetime.now().year-1, month=2, day=1)
        )
        res = self.client.get(
            OPERATIONS_URL,
            {
                'year': operation2.date.year,
                'month': operation2.date.month
            }
        )

        serializer1 = OperationSerializer(operation1)
        serializer2 = OperationSerializer(operation2)
        serializer3 = OperationSerializer(operation3)

        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_operation_by_year_month_day(self):
        """Test filtering operation by year and month"""
        operation1 = sample_operation(
            user=self.user,
            date=date(year=datetime.now().year-1, month=1, day=1)
        )
        operation2 = sample_operation(
            user=self.user,
            date=date(year=datetime.now().year-1, month=1, day=2)
        )
        operation3 = sample_operation(
            user=self.user,
            date=date(year=datetime.now().year-1, month=2, day=2)
        )
        res = self.client.get(
            OPERATIONS_URL,
            {
                'year': operation2.date.year,
                'month': operation2.date.month,
                'day': operation2.date.day
            }
        )

        serializer1 = OperationSerializer(operation1)
        serializer2 = OperationSerializer(operation2)
        serializer3 = OperationSerializer(operation3)

        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class AccountBalanceTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'sample_user@gmail.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)
        self.account = sample_account(user=self.user)

    def test_account_actual_balance(self):
        """Test the actual account balance"""
        value_list = []
        for i in range(100):
            value = round(Decimal(random.uniform(0.00, 100.00)), 2)
            value_list.append(value)
            sample_operation(
                user=self.user,
                account=self.account,
                value=value
            )
        expected_balance = round(Decimal(sum(value_list)), 2)
        url = account_balance_url(self.account.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_balance)

    def test_account_actual_balance_fail(self):
        """Test expecting http 400 bad request"""
        sample_operation(
            user=self.user,
            account=self.account
        )
        account = sample_account(user=self.user)
        url = account_balance_url(account.id+1)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_actual_balance_current_user(self):
        """Test actual balance for current user only"""
        operation1 = sample_operation(
            user=self.user,
            account=self.account,
            value=10.00
        )
        sample_operation(
            user=get_user_model().objects.create_user(
                'user2@gmail.com',
                'testpass123'
            ),
            account=self.account,
            value=-10.00
        )

        url = account_balance_url(self.account.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, operation1.value)

    def test_yearly_balance(self):
        """Test account yearly balance"""
        operation1 = sample_operation(
            user=self.user,
            account=self.account,
            value=50.00,
            date=date.today()
        )
        sample_operation(
            user=self.user,
            account=self.account,
            value=100.00,
            date=date(
                year=datetime.now().year-1,
                month=datetime.now().month,
                day=datetime.now().day
            )
        )
        url = account_balance_url(self.account.id)
        res = self.client.get(
            url,
            {
                'year': operation1.date.year
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, operation1.value)

    def test_monthly_balance(self):
        """Test account monthly balance"""
        operation1 = sample_operation(
            user=self.user,
            account=self.account,
            value=50.00,
            date=date.today()
        )
        sample_operation(
            user=self.user,
            account=self.account,
            value=100.00,
            date=date(
                year=datetime.now().year,
                month=datetime.now().month-1,
                day=datetime.now().day
            )
        )
        sample_operation(
            user=self.user,
            account=self.account,
            value=-1.00,
            date=date(
                year=datetime.now().year-1,
                month=datetime.now().month,
                day=datetime.now().day
            )
        )
        url = account_balance_url(self.account.id)
        res = self.client.get(
            url,
            {
                'year': operation1.date.year,
                'month': operation1.date.month
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, operation1.value)

    def test_dayly_balance(self):
        """Test account daily balance"""
        operation1 = sample_operation(
            user=self.user,
            account=self.account,
            value=50.00,
            date=date.today()
        )
        sample_operation(
            user=self.user,
            account=self.account,
            value=100.00,
            date=date(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day-1
            )
        )
        sample_operation(
            user=self.user,
            account=self.account,
            value=-1.00,
            date=date(
                year=datetime.now().year,
                month=datetime.now().month-1,
                day=datetime.now().day
            )
        )
        sample_operation(
            user=self.user,
            account=self.account,
            value=-10.00,
            date=date(
                year=datetime.now().year-1,
                month=datetime.now().month,
                day=datetime.now().day
            )
        )
        url = account_balance_url(self.account.id)
        res = self.client.get(
            url,
            {
                'year': operation1.date.year,
                'month': operation1.date.month,
                'day': operation1.date.day
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, operation1.value)
