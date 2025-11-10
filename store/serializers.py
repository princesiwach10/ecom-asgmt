# Related third-party imports
from rest_framework import serializers


class CartLineOutSerializer(serializers.Serializer):
    """
    Output shape for a single cart line.
    """

    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField()


class CartOutSerializer(serializers.Serializer):
    """
    Output payload for GET /api/cart/:
    Using DecimalField ensures DRF renders it as a string with two decimals.
    """

    items = CartLineOutSerializer(many=True)

    total = serializers.DecimalField(
        decimal_places=2,
        max_digits=10,
    )


class CartItemSerializer(serializers.Serializer):
    """
    Request payload to add or set a cart item.
    """

    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1,
    )


class ProductSerializer(serializers.Serializer):
    """
    Product payload for the public API.
    """

    id = serializers.IntegerField()

    name = serializers.CharField()

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
