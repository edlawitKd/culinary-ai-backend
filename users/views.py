from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User, DietaryProfile, HealthGoal, AllergyIntolerance
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserUpdateSerializer, DietaryProfileSerializer,
    HealthGoalSerializer, AllergyIntoleranceSerializer
)

# ---------------- User Registration ----------------
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------- User Login ----------------
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = timezone.now()
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------- User Logout ----------------
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ---------------- User Profile ----------------
class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        # Blacklist all tokens
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        except:
            pass
        return Response({'message': 'Account deactivated successfully'}, status=status.HTTP_200_OK)

# ---------------- Dietary Profile ----------------
class DietaryProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DietaryProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, _ = DietaryProfile.objects.get_or_create(user=self.request.user)
        return profile

# ---------------- Health Goal ----------------
class HealthGoalView(generics.RetrieveUpdateAPIView):
    serializer_class = HealthGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        goal, _ = HealthGoal.objects.get_or_create(user=self.request.user)
        return goal

# ---------------- Allergy CRUD ----------------
class AllergyIntoleranceListCreateView(generics.ListCreateAPIView):
    serializer_class = AllergyIntoleranceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AllergyIntolerance.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AllergyIntoleranceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AllergyIntoleranceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AllergyIntolerance.objects.filter(user=self.request.user)