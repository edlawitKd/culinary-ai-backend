from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


def default_expiry_date():
    return timezone.now().date() + timedelta(days=7)

class PantryItem(models.Model):
    CATEGORY_CHOICES = [
        ("vegetable", "Vegetable"),
        ("fruit", "Fruit"),
        ("dairy", "Dairy"),
        ("protein", "Protein"),
        ("spice", "Spice"),
        ("baking","Baking"),
        ("other", "Other"),
    ]
    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Liter"),
        ("ml", "Milliliter"),
        ("pcs", "Pieces"),
    ]
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="pantry_items"
    )

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other")
    quantity = models.FloatField()
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="pcs")
    expiry_date = models.DateField(default=default_expiry_date)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expiring_soon(self):
        return (self.expiry_date - timezone.now().date()).days <= 3

    def is_low_stock(self):
        return self.quantity <= 1

    def __str__(self):
        return self.name