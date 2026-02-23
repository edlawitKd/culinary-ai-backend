from django.contrib import admin
from .models import PantryItem

@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'user', 'expiry_date')