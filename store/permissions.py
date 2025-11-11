# Standard library imports
import secrets

# Related third-party imports
from django.conf import settings
from rest_framework.permissions import BasePermission


class HasAdminApiKey(BasePermission):
    """
    Require X-Admin-Key header to match settings.ADMIN_API_KEY.
    Keeps admin endpoints protected without a DB.
    """

    def has_permission(self, request, view):
        expected = settings.ADMIN_API_KEY
        provided = request.headers.get("X-Admin-Key")
        if not expected or not provided:
            return False
        return secrets.compare_digest(provided, expected)
