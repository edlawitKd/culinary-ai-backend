from rest_framework import serializers
from .models import PantryItem

class PantryItemSerializer(serializers.ModelSerializer):
    expiring_soon = serializers.SerializerMethodField()
    low_stock = serializers.SerializerMethodField()

    class Meta:
        model = PantryItem
        fields = "__all__"
        read_only_fields = ["user"]

    def get_expiring_soon(self, obj):
        return obj.is_expiring_soon()

    def get_low_stock(self, obj):
        return obj.is_low_stock()