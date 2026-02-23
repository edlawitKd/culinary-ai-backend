from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import Plan, Subscription, Payment
from .serializers import PlanSerializer, SubscriptionSerializer, PaymentSerializer

# ---------------- Plans ----------------
class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

# ---------------- Subscriptions ----------------
class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

# ---------------- Payment history ----------------
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(subscription__user=self.request.user)


# ---------------- Create Telebirr Payment (or free plan activation) ----------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_telebirr_payment(request):
    user = request.user
    plan_id = request.data.get('plan_id')
    plan = get_object_or_404(Plan, id=plan_id)

    # -------- Free plan --------
    if plan.name.lower() == "free":
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            is_active=True,
            start_date=timezone.now()
        )
        return Response({"message": "Free plan activated successfully."})

    # -------- Paid plan --------
    # Create subscription in pending state
    subscription = Subscription.objects.create(
    user=user,
    plan=plan,
    is_active=False,
    start_date=None  # explicitly None for now
)

    # Create pending payment record
    payment = Payment.objects.create(
        subscription=subscription,
        amount=plan.price,
        status='pending',
    )

    # -------- Mock Telebirr URL --------
    # Replace with real Telebirr API call once credentials are ready
    mock_payment_url = f"http://localhost:3000/mock_payment/{payment.id}/"

    return Response({
        "payment_url": mock_payment_url,
        "payment_id": payment.id
    })


# ---------------- Telebirr Callback ----------------
@api_view(['POST'])
def telebirr_callback(request):
    """
    Telebirr calls this endpoint to confirm payment.
    Payload: { order_id, status }
    """
    order_id = request.data.get('order_id')
    status_ = request.data.get('status')  # 'success' / 'failed'

    payment = Payment.objects.filter(id=order_id).first()
    if not payment:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    subscription = payment.subscription

    if status_ == 'success':
        payment.status = 'completed'
        payment.save()

        # Activate subscription
        subscription.is_active = True
        subscription.start_date = subscription.start_date or timezone.now()
        subscription.save()  # end_date will calculate automatically in model
    else:
        payment.status = 'failed'
        payment.save()

    return Response({"message": "Payment status updated"})