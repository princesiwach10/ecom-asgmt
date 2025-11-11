# Related third-party imports
from django.urls import path

# Local application/library specific imports
from .views import (
    AdminGenerateDiscount,
    AdminStats,
    CartItemAdd,
    CartItemUpdate,
    CartView,
    Checkout,
    HealthView,
    ProductList,
)


urlpatterns = [
    path(
        "admin/generate-discount/",
        AdminGenerateDiscount.as_view(),
        name="admin-generate-discount",
    ),
    path(
        "admin/stats/",
        AdminStats.as_view(),
        name="admin-stats",
    ),
    path(
        "cart/",
        CartView.as_view(),
        name="cart",
    ),
    path(
        "cart/items/",
        CartItemAdd.as_view(),
        name="cart-add",
    ),
    path(
        "cart/items/<int:product_id>/",
        CartItemUpdate.as_view(),
        name="cart-item",
    ),
    path(
        "checkout/",
        Checkout.as_view(),
        name="checkout",
    ),
    path(
        "health/",
        HealthView.as_view(),
        name="health",
    ),
    path(
        "products/",
        ProductList.as_view(),
        name="products",
    ),
]
