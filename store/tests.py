# Standard library imports
import json

# Related third-party imports
from django.test import TestCase
from django.urls import reverse


def J(resp):
    return json.loads(resp.content.decode())


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
            HTTP_X_USER_ID="U3",
        )
        r = self.client.delete(
            reverse("cart-item", kwargs={"product_id": 3}),
            HTTP_X_USER_ID="U3",
        )
        self.assertEqual(r.status_code, 204)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U3")
        self.assertEqual(J(r)["items"], [])

    def test_add_and_get_cart_total(self):
        r = self.client.post(
            reverse("cart-add"),
            data={"product_id": 1, "quantity": 2},
            content_type="application/json",
            HTTP_X_USER_ID="U1",
        )
        self.assertEqual(r.status_code, 201)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(J(r)["total"], "1500.00")

    def test_put_sets_qty_and_zero_removes(self):
        # Add once
        self.client.post(
            reverse("cart-add"),
            data={"product_id": 2, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="U2",
        )
        # Set to 3
        r = self.client.put(
            reverse("cart-item", kwargs={"product_id": 2}),
            data={"quantity": 3},
            content_type="application/json",
            HTTP_X_USER_ID="U2",
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U2")
        self.assertEqual(J(r)["items"][0]["quantity"], 3)

        # Set to 0 -> removes
        r = self.client.put(
            reverse("cart-item", kwargs={"product_id": 2}),
            data={"quantity": 0},
            content_type="application/json",
            HTTP_X_USER_ID="U2",
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse("cart"), HTTP_X_USER_ID="U2")
        self.assertEqual(J(r)["items"], [])

    def test_validation_unknown_product_and_bad_qty(self):
        # Unknown product_id
        r = self.client.post(
            reverse("cart-add"),
            data={"product_id": 999, "quantity": 1},
            content_type="application/json",
            HTTP_X_USER_ID="U4",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("Unknown product_id", J(r)["detail"])

        # Bad qty type
        r = self.client.put(
            reverse("cart-item", kwargs={"product_id": 1}),
            data={"quantity": "abc"},
            content_type="application/json",
            HTTP_X_USER_ID="U4",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("quantity must be an integer", J(r)["detail"])


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
