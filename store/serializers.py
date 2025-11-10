# Related third-party imports
from rest_framework import serializers


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
