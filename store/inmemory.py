"""
Lightweight, in-memory data store for the e-commerce demo.

This module intentionally avoids a database to satisfy the assignment
requirements.
"""

# Standard library imports
import secrets
import string
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

# Related third-party imports
from django.conf import settings
from django.utils import timezone


def D(x) -> Decimal:
    """
    Return a Decimal from any numeric/string value with safe coercion.
    """
    return Decimal(str(x))


def money(x: Decimal) -> Decimal:
    """
    Two-decimal rounding suitable for currency display and arithmetic.
    """
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _isoz(dt: datetime) -> str:
    """
    ISO-8601 with 'Z' for UTC (e.g., 2025-11-10T15:20:30.123456Z).
    Keeps external API stable while using timezone-aware datetimes internally.
    """
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class Product:
    """
    Represents a simple, sellable product in our in-memory catalog.
    """

    id: int
    name: str
    price: Decimal


@dataclass(frozen=True)
class OrderItem:
    """
    Immutable snapshot of a purchased item.
    We snapshot name & price so past orders aren't affected by catalog changes.
    """

    product_id: int
    name: str
    price: Decimal
    quantity: int
    line_total: Decimal


@dataclass
class Order:
    """
    A completed order (cart -> order conversion).
    """

    id: int
    user_id: str
    items: List[OrderItem]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    created_at: datetime
    discount_code: Optional[str] = None


@dataclass
class DiscountCode:
    """
    Represents a single-use discount code that applies to the entire order.
    """

    code: str
    created_at: datetime
    used: bool = False
    redeemed_order_id: Optional[int] = None
    discount_pct: int = 10  # default 10%


class InMemoryStore:
    """
    An in-memory, process-local data store.

    Attributes
    ----------
    products : Dict[int, Product]
        A tiny fixed catalog for the demo.

    carts : Dict[str, Dict[int, int]]
        Per-user carts: user_id -> { product_id: quantity }

    orders : list[Order]
        All placed orders.
    """

    def __init__(self):
        # A tiny product catalog;
        self.products: Dict[int, Product] = {
            1: Product(1, "Almonds 500g", D("750")),
            2: Product(2, "Cashews 500g", D("350")),
            3: Product(3, "Pistachios 500g", D("900")),
        }
        # user carts stored in-memory
        self.carts: Dict[str, Dict[int, int]] = {}
        # orders placed in-memory
        self.orders: List[Order] = []
        # Discount state
        self.discount_codes: List[DiscountCode] = []
        self.active_code: Optional[str] = None  # currently-available single-use code

    # Cart helpers -----

    def add_to_cart(self, user_id: str, product_id: int, quantity: int) -> None:
        """
        Increment a product's quantity in the user's cart.
        """
        if product_id not in self.products:
            raise ValueError("Unknown product_id")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        cart = self.get_cart(user_id)
        qty = cart.get(product_id, 0) + quantity
        cart[product_id] = qty

    def clear_cart(self, user_id: str) -> None:
        """
        Remove all items in the user's cart.
        """
        self.carts[user_id] = {}

    def get_cart(self, user_id: str) -> Dict[int, int]:
        """
        Return the user's cart dict (creating it if absent).
        """
        return self.carts.setdefault(user_id, {})

    def remove_cart_item(self, user_id: str, product_id: int) -> None:
        """
        Remove a product from the user's cart (no error if absent).
        """
        self.get_cart(user_id).pop(product_id, None)

    def set_cart_item(self, user_id: str, product_id: int, quantity: int) -> None:
        """
        Set a product's quantity exactly. If quantity <= 0, remove the item.
        """
        cart = self.get_cart(user_id)
        if quantity <= 0:
            cart.pop(product_id, None)
            return

        if product_id not in self.products:
            raise ValueError("Unknown product_id")

        cart[product_id] = quantity

    # Order creation/Checkout Helpers -----

    def place_order(self, user_id: str, discount_code: Optional[str] = None) -> Order:
        """
        Convert the current cart into an Order and clear the cart.
        Applies discount if a valid code is provided.
        """
        cart = self.get_cart(user_id)
        if not cart:
            raise ValueError("Cart is empty")

        items: List[OrderItem] = []
        subtotal = D("0.00")
        for pid, qty in cart.items():
            product = self.products.get(pid)
            if not product:
                continue
            line_total = money(product.price * D(qty))
            items.append(
                OrderItem(
                    product_id=pid,
                    name=product.name,
                    price=product.price,
                    quantity=qty,
                    line_total=line_total,
                )
            )
            subtotal += line_total
        subtotal = money(subtotal)

        discount = D("0.00")
        applied_code = None
        if discount_code and self.validate_discount(discount_code):
            applied_code = discount_code
            pct = D(self._find_code(discount_code).discount_pct)
            discount = money(subtotal * (pct / D(100)))

        total = money(subtotal - discount)

        order = Order(
            id=len(self.orders) + 1,
            user_id=user_id,
            items=items,
            subtotal=subtotal,
            discount=discount,
            total=total,
            created_at=timezone.now(),
            discount_code=applied_code,
        )
        self.orders.append(order)
        self.clear_cart(user_id)

        # Mark discount as consumed
        if applied_code:
            dc = self._find_code(applied_code)
            dc.used = True
            dc.redeemed_order_id = order.id
            self.active_code = None  # consume current active code

        return order

    # Order index helpers -----
    def next_order_number(self) -> int:
        """
        The order number that will be assigned to the next order placed.
        """
        return len(self.orders) + 1

    def eligible_now(self) -> bool:
        """
        True if the very next order is eligible for a discount
        (i.e., (next_order_number % N) == 0).
        """
        n = settings.NTH_ORDER_FOR_DISCOUNT
        return self.next_order_number() % n == 0

    # Discount helpers -----
    def has_active_code(self) -> bool:
        """
        True if an unconsumed code has been generated and is active.
        """
        return self.active_code is not None

    def _random_code(self, length: int = 8) -> str:
        """
        Generate an 8-char A-Z0-9 code.
        """
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def generate_code(self) -> DiscountCode:
        """
        Generate a discount code (single-use) when eligible and no active code exists.
        Side-effect: sets self.active_code.
        """
        code = self._random_code()
        dc = DiscountCode(
            code=code, created_at=timezone.now(), discount_pct=settings.DISCOUNT_PERCENT
        )
        self.discount_codes.append(dc)
        self.active_code = code
        return dc

    def _find_code(self, code: str) -> DiscountCode:
        """
        Find the most recent instance of a code or raise.
        """
        for dc in reversed(self.discount_codes):
            if dc.code == code:
                return dc
        raise ValueError("Code not found")

    def validate_discount(self, code: Optional[str]) -> bool:
        """
        A code is valid iff:
        - matches the current active_code,
        - the next order is eligible (nth), and
        - the code hasn't been used yet.
        """
        if not code:
            return False

        if code != self.active_code:
            return False

        if not self.eligible_now():
            return False

        try:
            dc = self._find_code(code)
        except ValueError:
            return False

        return not dc.used

    # Admin stats -----
    def stats(self) -> Dict[str, object]:
        """
        Aggregate purchase stats and list discount codes.
        """
        items_count = sum(oi.quantity for o in self.orders for oi in o.items)
        gross = sum(o.subtotal for o in self.orders) if self.orders else D("0.00")
        total_discount = (
            sum(o.discount for o in self.orders) if self.orders else D("0.00")
        )
        net = sum(o.total for o in self.orders) if self.orders else D("0.00")

        return {
            "items_purchased": items_count,
            "gross_amount": money(gross),
            "total_discount_amount": money(total_discount),
            "net_amount": money(net),
            "discount_codes": [
                {
                    "code": dc.code,
                    "used": dc.used,
                    "discount_pct": dc.discount_pct,
                    "redeemed_order_id": dc.redeemed_order_id,
                    "created_at": _isoz(dc.created_at),
                }
                for dc in self.discount_codes
            ],
        }


# Module-level singleton used by views. It keeps state for the process.
db = InMemoryStore()
