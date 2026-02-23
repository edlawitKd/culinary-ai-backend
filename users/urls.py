from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, DietaryProfileView, HealthGoalView,
    AllergyIntoleranceListCreateView, AllergyIntoleranceDetailView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/dietary/', DietaryProfileView.as_view(), name='dietary-profile'),
    path('profile/health-goal/', HealthGoalView.as_view(), name='health-goal'),
    path('profile/allergies/', AllergyIntoleranceListCreateView.as_view(), name='allergy-list'),
    path('profile/allergies/<int:pk>/', AllergyIntoleranceDetailView.as_view(), name='allergy-detail'),
]