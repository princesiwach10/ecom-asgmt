from django.test import TestCase
from django.urls import reverse
import json


class HealthTests(TestCase):
    def test_health(self):
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode()), {"status": "ok"})
