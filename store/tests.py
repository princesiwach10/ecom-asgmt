# Standard library imports
import json
from importlib import reload

# Related third-party imports
from django.conf import settings
from django.test import override_settings, TestCase
from django.urls import reverse

# Local application/library specific imports
from store import inmemory, views


def J(resp):
    return json.loads(resp.content.decode())


class BaseStoreTest(TestCase):
    def setUp(self):
        # Reinitialize the singleton so orders/carts/codes are wiped
        reload(inmemory)
        views.db = inmemory.db


class AdminAuthTests(TestCase):

    def test_admin_requires_key(self):
        r = self.client.post(reverse("admin-generate-discount"))
        self.assertEqual(r.status_code, 403)

    def test_admin_with_key(self):
        r = self.client.post(
            reverse("admin-generate-discount"), **{"HTTP_X_ADMIN_KEY": "supersecret"}
        )
        self.assertIn(r.status_code, (200, 201, 400))


class CartAPITests(TestCase):
    """
    Verifies core cart behaviors:
    - add -> shows in GET /cart with correct total
    - put -> sets qty; <=0 removes
    - delete -> removes
    - validation -> unknown product, bad qty
    """

    def test_delete_removes(self):
        self.client.post(
            reverse("cart-add"),
            data={"product_id": 3, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_1",
        )
        r = self.client.delete(
            reverse("cart-item", kwargs={"product_id": 3}),
            HTTP_X_USER_ID="U1_Cart_1",
        )
        self.assertEqual(r.status_code, 204)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U1_Cart_1")
        self.assertEqual(J(r)["items"], [])

    def test_add_and_get_cart_total(self):
        r = self.client.post(
            reverse("cart-add"),
            data={"product_id": 1, "quantity": 2},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_2",
        )
        self.assertEqual(r.status_code, 201)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U1_Cart_2")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(J(r)["total"], "1500.00")

    def test_put_sets_qty_and_zero_removes(self):
        # Add once
        self.client.post(
            reverse("cart-add"),
            data={"product_id": 2, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_3",
        )
        # Set to 3
        r = self.client.put(
            reverse("cart-item", kwargs={"product_id": 2}),
            data={"quantity": 3},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_3",
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U1_Cart_3")
        self.assertEqual(J(r)["items"][0]["quantity"], 3)

        # Set to 0 -> removes
        r = self.client.put(
            reverse("cart-item", kwargs={"product_id": 2}),
            data={"quantity": 0},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_3",
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U1_Cart_3")
        self.assertEqual(J(r)["items"], [])

    def test_validation_unknown_product_and_bad_qty(self):
        # Unknown product_id
        r = self.client.post(
            reverse("cart-add"),
            data={"product_id": 999, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_4",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("Unknown product_id", J(r)["detail"])

        # Bad qty type
        r = self.client.put(
            reverse("cart-item", kwargs={"product_id": 1}),
            data={"quantity": "abc"},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Cart_4",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("quantity must be an integer", J(r)["detail"])


class CheckoutAPITests(TestCase):
    """
    Verifies checkout behavior (without discounts).
    """

    def test_checkout_success_clears_cart_and_returns_order(self):
        r = self.client.post(
            reverse("cart-add"),
            data={"product_id": 1, "quantity": 2},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Checkout_1",
        )

        self.assertEqual(r.status_code, 201)

        r = self.client.post(
            reverse("checkout"),
            data={},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Checkout_1",
        )
        self.assertEqual(r.status_code, 201)
        order = J(r)
        self.assertEqual(order["subtotal"], "1500.00")
        self.assertEqual(order["discount"], "0.00")
        self.assertEqual(order["total"], "1500.00")
        self.assertIsNone(order.get("discount_code"))

        # Cart should be cleared
        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U1_Checkout_1")
        self.assertEqual(J(r)["items"], [])

    def test_checkout_rejects_discount_code(self):
        self.client.post(
            reverse("cart-add"),
            data={"product_id": 2, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Checkout_2",
        )

        r = self.client.post(
            reverse("checkout"),
            data={"discount_code": "ABC123"},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Checkout_2",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("Discount not available for order.", J(r)["detail"])

    def test_checkout_empty_cart(self):
        r = self.client.post(
            reverse("checkout"),
            data={},
            content_type="application/json",
            HTTP_X_USER_ID="U1_Checkout_3",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("Cart is empty", J(r)["detail"])


@override_settings(ADMIN_API_KEY="test-key")
class DiscountFlowTests(TestCase):
    """
    Verifies:
    - discount code can be generated only when next order is Nth
    - code is single-use
    - code applies 10% to entire order
    """

    def setUp(self):
        # Reinitialize the singleton so orders/carts/codes are wiped
        reload(inmemory)
        views.db = inmemory.db

        # admin auth header for all admin endpoints
        self.admin = {"HTTP_X_ADMIN_KEY": "test-key"}

    def test_discount_only_on_nth_order_and_single_use(self):
        n = settings.NTH_ORDER_FOR_DISCOUNT

        # Place (n-1) orders (without discount) to reach eligibility
        for i in range(1, n):
            uid = f"pre{i}"
            self.client.post(
                reverse("cart-add"),
                data={"product_id": 1, "quantity": 1},
                content_type="application/json",
                HTTP_X_USER_ID=uid,
            )
            self.client.post(
                reverse("checkout"),
                data={},
                content_type="application/json",
                HTTP_X_USER_ID=uid,
            )

        # Now eligible; generate a code
        r = self.client.post(reverse("admin-generate-discount"), **self.admin)
        self.assertEqual(r.status_code, 201)
        code = J(r)["code"]

        # Build an eligible order using the code
        self.client.post(
            reverse("cart-add"),
            data={"product_id": 2, "quantity": 2},
            content_type="application/json",
            HTTP_X_USER_ID="nth-user",
        )
        r = self.client.post(
            reverse("checkout"),
            data={"discount_code": code},
            content_type="application/json",
            HTTP_X_USER_ID="nth-user",
        )
        self.assertEqual(r.status_code, 201)
        order = J(r)
        self.assertEqual(order["discount_code"], code)
        # sanity: product 2 is 350 -> 2 * 350 = 700, 10% discount = 70, total = 630
        self.assertEqual(order["subtotal"], "700.00")
        self.assertEqual(order["discount"], "70.00")
        self.assertEqual(order["total"], "630.00")

        # Reuse the same code should fail
        self.client.post(
            reverse("cart-add"),
            data={"product_id": 2, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="another",
        )
        r2 = self.client.post(
            reverse("checkout"),
            data={"discount_code": code},
            content_type="application/json",
            HTTP_X_USER_ID="another",
        )
        self.assertEqual(r2.status_code, 400)

    def test_cannot_generate_code_when_not_eligible(self):
        # Fresh run; first order is not eligible if N > 1
        r = self.client.post(reverse("admin-generate-discount"), **self.admin)
        if settings.NTH_ORDER_FOR_DISCOUNT > 1:
            self.assertEqual(r.status_code, 400)

    def test_admin_stats_basic(self):
        # Place two orders
        for uid in ["s1", "s2"]:
            self.client.post(
                reverse("cart-add"),
                data={"product_id": 1, "quantity": 1},
                content_type="application/json",
                HTTP_X_USER_ID=uid,
            )
            self.client.post(
                reverse("checkout"),
                data={},
                content_type="application/json",
                HTTP_X_USER_ID=uid,
            )

        r = self.client.get(reverse("admin-stats"), **self.admin)
        self.assertEqual(r.status_code, 200)
        stats = J(r)
        self.assertIn("items_purchased", stats)
        self.assertIn("discount_codes", stats)


class HealthTests(TestCase):
    def test_health(self):
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode()), {"status": "ok"})


class ProductAPITests(TestCase):
    """
    Verifies the public product catalog is exposed and shaped correctly.
    """

    def test_get_products(self):
        resp = self.client.get(reverse("products"))
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.content.decode())

        # Basic shape checks
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        for item in data:
            self.assertIn("id", item)
            self.assertIn("name", item)
            self.assertIn("price", item)

            # price should be a stringified decimal with two places
            self.assertRegex(item["price"], r"^\d+\.\d{2}$")
