from rest_framework import serializers

from core.models import Account, AccountType, Tag, Operation


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


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)


class OperationSerializer(serializers.ModelSerializer):
    """Serializer for operation object"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all()
    )

    class Meta:
        model = Operation
        fields = (
            'id', 'name', 'description', 'value', 'date', 'tags', 'account'
            )
        read_only_fields = ('id',)


class OperationDetailSerializer(OperationSerializer):
    """Serialize an operation detail"""
    account = AccountSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
