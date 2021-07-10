from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Account, AccountType, Tag, Operation

from operation import serializers


class AccountTypeViewSet(viewsets.ModelViewSet):
    """Manage account types in the database"""
    queryset = AccountType.objects.all()
    serializer_class = serializers.AccountTypeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        queryset = self.queryset

        return queryset.filter(
            user=self.request.user
        ).order_by('name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class AccountViewSet(viewsets.ModelViewSet):
    """Manage account in the database"""
    queryset = Account.objects.all()
    serializer_class = serializers.AccountSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the accounts for the authenticated user"""
        queryset = self.queryset

        return queryset.filter(
            user=self.request.user
        ).order_by('name').distinct()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.AccountDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """Manage tag in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        queryset = self.queryset

        return queryset.filter(
            user=self.request.user
        ).order_by('name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class OperationViewSet(viewsets.ModelViewSet):
    """Manage operation in the database"""
    queryset = Operation.objects.all()
    serializer_class = serializers.OperationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the operations for the authenticated user"""
        tags = self.request.query_params.get('tags')
        account = self.request.query_params.get('account')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')

        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if account:
            account_id = self._params_to_ints(account)
            queryset = queryset.filter(account__id__in=account_id)
        if year:
            queryset = queryset.filter(date__year=year)
        if year and month:
            queryset = queryset.filter(date__year=year, date__month=month)
        if year and month and day:
            queryset = queryset.filter(
                date__year=year, date__month=month, date__day=day
            )
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.OperationDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new operation"""
        serializer.save(user=self.request.user)
