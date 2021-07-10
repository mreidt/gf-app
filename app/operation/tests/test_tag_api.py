from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from operation.serializers import TagSerializer

TAG_URL = reverse('operation:tag-list')


def sample_tag(user, name='Samlpe tag'):
    """Create and return a sample tag object"""
    return Tag.objects.create(
        user=user,
        name=name
    )


class PublicTagApiTests(TestCase):
    """Test the puclicly available Tag API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access endpoint"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test the private Tag API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tag_list(self):
        """Test retrieving a list of tags"""
        sample_tag(user=self.user)
        sample_tag(user=self.user, name='Tag number 2')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test retrieving tags for user"""
        user2 = get_user_model().objects.create_user(
            'doctorWho@gmail.com',
            'pass123'
        )
        sample_tag(user=user2, name='Tag user2')
        tag = sample_tag(user=self.user)

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a tag successfully"""
        payload = {'name': 'My new tag', 'user': self.user}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating an invalid tag"""
        payload = {'name': '', 'user_id': self.user.id}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
