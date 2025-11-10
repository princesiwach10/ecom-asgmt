from django.urls import path
from .views import HealthView, ProductList

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("products/", ProductList.as_view(), name="products"),
]
