from django.contrib import admin
from .models import Plan, Subscription, Payment

# -------------------------
# Plan Admin
# -------------------------
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active', 'duration_days')
    search_fields = ('name',)
    ordering = ('price',)


# -------------------------
# Subscription Admin
# -------------------------
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('user__username', 'plan__name')
    ordering = ('-start_date',)


# -------------------------
# Payment Admin
# -------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'status', 'timestamp', 'transaction_id')
    list_filter = ('status',)
    search_fields = ('subscription__user__username', 'transaction_id')
    ordering = ('-timestamp',)