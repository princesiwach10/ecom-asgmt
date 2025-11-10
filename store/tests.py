# Standard library imports
import json

# Related third-party imports
from django.test import TestCase
from django.urls import reverse


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
