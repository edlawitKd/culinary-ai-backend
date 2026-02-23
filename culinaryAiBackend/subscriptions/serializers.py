from rest_framework import serializers
from .models import Plan, Subscription, Payment

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all(), source='plan', write_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "user", "plan", "plan_id", "start_date", "end_date", "is_active"]


class PaymentSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)
    subscription_id = serializers.PrimaryKeyRelatedField(queryset=Subscription.objects.all(), source='subscription', write_only=True)

    class Meta:
        model = Payment
        fields = ["id", "subscription", "subscription_id", "amount", "timestamp", "transaction_id", "status"]