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


class CheckoutSerializer(serializers.Serializer):
    """
    Request payload for checkout.
    """

    discount_code = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


class OrderItemSerializer(serializers.Serializer):
    """
    Output payload for a single order item.
    """

    product_id = serializers.IntegerField()

    name = serializers.CharField()

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    quantity = serializers.IntegerField()

    line_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class OrderSerializer(serializers.Serializer):
    """
    Output payload for a completed order.
    """

    id = serializers.IntegerField()

    user_id = serializers.CharField()

    items = OrderItemSerializer(many=True)

    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    discount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    created_at = serializers.DateTimeField()

    discount_code = serializers.CharField(
        allow_null=True,
        required=False,
    )


class AdminStatsSerializer(serializers.Serializer):
    """
    Admin roll-up for purchases and discount codes.
    """

    items_purchased = serializers.IntegerField()

    gross_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total_discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    net_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    discount_codes = serializers.ListField()


class HealthSerializer(serializers.Serializer):
    """
    Simple health response.
    """

    status = serializers.CharField()


class AdminGenerateDiscountResponseSerializer(serializers.Serializer):
    """
    Schema for the admin generate-discount response.
    """

    code = serializers.CharField()

    created_at = serializers.CharField()

    discount_pct = serializers.IntegerField()

    note = serializers.CharField()
