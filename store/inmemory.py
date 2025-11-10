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
    """

    def __init__(self):
        self.products: Dict[int, Product] = {
            1: Product(1, "Almonds 500g", D("750")),
            2: Product(2, "Cashews 500g", D("350")),
            3: Product(3, "Pistachios 500g", D("900")),
        }


# Module-level singleton used by views. It keeps state for the process.
db = InMemoryStore()
