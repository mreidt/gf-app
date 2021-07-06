from rest_framework import serializers

from core.models import AccountType


class AccountTypeSerializer(serializers.ModelSerializer):
    """Serializer for account type object"""

    class Meta:
        model = AccountType
        fields = ('id', 'name', 'description', 'calculate')
        read_only_fields = ('id',)
# class IngredientSerializer(serializers.ModelSerializer):
#     """Serializer for ingredient object"""

#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name')
#         read_only_fiels = ('id',)
