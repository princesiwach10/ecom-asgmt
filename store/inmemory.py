"""
Lightweight, in-memory data store for the e-commerce demo.

This module intentionally avoids a database to satisfy the assignment
requirements.
"""

# Standard library imports
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


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


@dataclass
class Product:
    """
    Represents a simple, sellable product in our in-memory catalog.
    """

    id: int
    name: str
    price: Decimal


class InMemoryStore:
    """
    An in-memory, process-local data store.

    Attributes
    ----------
    products : Dict[int, Product]
        A tiny fixed catalog for the demo.

    carts : Dict[str, Dict[int, int]]
        Per-user carts: user_id -> { product_id: quantity }
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
        cart[product_id] = cart.get(product_id, 0) + quantity

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


# Module-level singleton used by views. It keeps state for the process.
db = InMemoryStore()
