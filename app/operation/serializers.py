from rest_framework import serializers

from core.models import Account, AccountType


class AccountTypeSerializer(serializers.ModelSerializer):
    """Serializer for account type object"""

    class Meta:
        model = AccountType
        fields = ('id', 'name', 'description', 'calculate')
        read_only_fields = ('id',)


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for account object"""
    acctype = serializers.PrimaryKeyRelatedField(
        queryset=AccountType.objects.all()
    )

    class Meta:
        model = Account
        fields = ('id', 'name', 'active', 'acctype')
        read_only_fields = ('id',)


class AccountDetailSerializer(AccountSerializer):
    """Serialize a account detail"""
    acctype = AccountTypeSerializer()
