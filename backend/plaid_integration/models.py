from django.conf import settings
from django.db import models


class PlaidItem(models.Model):
    """One linked brokerage login (a Plaid Item) for a user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="plaid_items")
    item_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)  # TODO: encrypt before production
    institution_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.institution_name or self.item_id}"
