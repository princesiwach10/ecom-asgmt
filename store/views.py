# Related third-party imports
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application/library specific imports
from .inmemory import db, D, money
from .permissions import HasAdminApiKey
from .serializers import (
    AdminStatsSerializer,
    CartItemSerializer,
    CartOutSerializer,
    CheckoutSerializer,
    OrderSerializer,
    ProductSerializer,
)


def get_user_id(request) -> str:
    """
    Derive a user identifier from headers.
    """
    return request.headers.get("X-User-Id", "u1")


class CartItemAdd(APIView):
    """
    POST /api/cart/items/
    Adds to the cart (increments existing quantity).
    """

    def post(self, request):
        user_id = get_user_id(request)
        ser = CartItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            db.add_to_cart(
                user_id,
                ser.validated_data["product_id"],
                ser.validated_data["quantity"],
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Item added to cart."},
            status=status.HTTP_201_CREATED,
        )


class CartItemUpdate(APIView):
    """
    PUT sets the exact quantity. A quantity <= 0 removes the item.
    DELETE removes the item explicitly.
    """

    def delete(self, request, product_id: int):
        user_id = get_user_id(request)
        db.remove_cart_item(user_id, int(product_id))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, product_id: int):
        user_id = get_user_id(request)
        qty = request.data.get("quantity", None)

        # Validate presence and integer-ness of quantity
        if qty is None:
            return Response(
                {"detail": "quantity is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            qty = int(qty)
        except Exception:
            return Response(
                {"detail": "quantity must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            db.set_cart_item(user_id, int(product_id), qty)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Cart updated."})


class CartView(APIView):
    """
    GET /api/cart/
    Returns the current user's cart and a computed total.
    """

    def get(self, request):
        user_id = get_user_id(request)
        cart = db.get_cart(user_id)

        items = []
        total = D("0.00")
        for pid, qty in cart.items():
            prod = db.products.get(pid)
            if not prod:
                continue
            line = money(prod.price * D(qty))
            items.append({"product_id": pid, "quantity": qty})
            total += line

        res_data = {"items": items, "total": money(total)}
        return Response(CartOutSerializer(res_data).data)


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


class Checkout(APIView):
    """
    POST /api/checkout/
    """

    def post(self, request):
        user_id = get_user_id(request)
        ser = CheckoutSerializer(data=request.data or {})
        ser.is_valid(raise_exception=True)
        code = ser.validated_data.get("discount_code") or None

        # If client sends a code, validate it before attempting checkout.
        if code and not db.validate_discount(code):
            if not db.eligible_now():
                return Response(
                    {"detail": f"Discount not available for order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "Invalid or unavailable discount code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = db.place_order(user_id, discount_code=code)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class AdminGenerateDiscount(APIView):
    """
    POST /api/admin/generate-discount/

    Generates a single-use discount code only when:
    - the next order is the Nth (eligible_now), and
    - no active code already exists.
    """

    permission_classes = [HasAdminApiKey]

    def post(self, request):
        if not db.eligible_now():
            n = settings.NTH_ORDER_FOR_DISCOUNT
            return Response(
                {
                    "detail": f"Not eligible yet. A code is available only for every {n}th order."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if db.has_active_code():
            return Response(
                {"detail": "An active discount code already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dc = db.generate_code()
        return Response(
            {
                "code": dc.code,
                "discount_pct": dc.discount_pct,
                "created_at": dc.created_at.isoformat().replace("+00:00", "Z"),
                "note": "Share this code with users. It will be valid for the next eligible (nth) order and is single-use.",
            },
            status=status.HTTP_201_CREATED,
        )


class AdminStats(APIView):
    """
    GET /api/admin/stats/

    Returns:
    - items_purchased
    - gross_amount
    - total_discount_amount
    - net_amount
    - discount_codes[] (with used, redeemed_order_id, created_at, etc.)
    """

    permission_classes = [HasAdminApiKey]

    def get(self, request):
        stats = db.stats()
        return Response(AdminStatsSerializer(stats).data)
