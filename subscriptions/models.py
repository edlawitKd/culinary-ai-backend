from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

# Plan Model
class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# User Subscription
class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions"  # <- Unique related_name
    )
    plan = models.ForeignKey('subscriptions.Plan', on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.start_date and self.plan and getattr(self.plan, "duration_days", None):
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

# Payment History
class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending","Pending"),("completed","Completed"),("failed","Failed")],
        default="pending"
    )

    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount} - {self.status}"