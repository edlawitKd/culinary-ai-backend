from .views import PlanViewSet, SubscriptionViewSet, PaymentViewSet, create_telebirr_payment, telebirr_callback
from django.urls import path

urlpatterns = [
    # Plans
    path('plans/', PlanViewSet.as_view({'get': 'list'}), name='plan-list'),
    path('plans/<int:pk>/', PlanViewSet.as_view({'get': 'retrieve'}), name='plan-detail'),

    # Subscriptions
    path('subscriptions/', SubscriptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='subscription-list'),
    path('subscriptions/<int:pk>/', SubscriptionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='subscription-detail'),

    # Payments
    path('payments/', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment-list'),
    path('payments/<int:pk>/', PaymentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='payment-detail'),

    # Telebirr
    path('create_telebirr_payment/', create_telebirr_payment, name='create-telebirr-payment'),
    path('telebirr_callback/', telebirr_callback, name='telebirr-callback'),
]