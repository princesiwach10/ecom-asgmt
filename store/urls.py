# Related third-party imports
from django.urls import path

# Local application/library specific imports
from .views import CartItemAdd, CartItemUpdate, CartView, HealthView, ProductList


urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/items/", CartItemAdd.as_view(), name="cart-add"),
    path("cart/items/<int:product_id>/", CartItemUpdate.as_view(), name="cart-item"),
    path("health/", HealthView.as_view(), name="health"),
    path("products/", ProductList.as_view(), name="products"),
]
