# Related third-party imports
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application/library specific imports
from .inmemory import db, money
from .serializers import ProductSerializer


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class ProductList(APIView):
    """
    GET /api/products/
    Returns a simple list of products from the in-memory catalog.
    """

    def get(self, request):
        # Prepare a plain list from in-memory db.
        data = [
            {"id": p.id, "name": p.name, "price": money(p.price)}
            for p in db.products.values()
        ]

        # then serializer validate/shape
        serializer = ProductSerializer(data, many=True)
        return Response(serializer.data)
