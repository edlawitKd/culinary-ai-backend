from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, DietaryProfile, HealthGoal, AllergyIntolerance, UserSubscription, SubscriptionPlan

# ---------------- User Serializers ----------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        
        # Create empty profiles
        DietaryProfile.objects.create(user=user)
        HealthGoal.objects.create(user=user)
        
        # Create Free Trial subscription
        trial_plan, _ = SubscriptionPlan.objects.get_or_create(name="Free Trial", price=0, duration_days=7)
        UserSubscription.objects.create(user=user, plan=trial_plan, is_trial=True)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    if user.is_active:
                        data['user'] = user
                    else:
                        raise serializers.ValidationError("User account is disabled")
                else:
                    raise serializers.ValidationError("Invalid password")
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'")
        return data

# ---------------- Profile & Related Serializers ----------------
class AllergyIntoleranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergyIntolerance
        fields = ['id', 'allergy_type', 'severity', 'specific_notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class DietaryProfileSerializer(serializers.ModelSerializer):
    allergies = AllergyIntoleranceSerializer(source='user.allergies', many=True, read_only=True)
    
    class Meta:
        model = DietaryProfile
        fields = ['id', 'dietary_preference', 'custom_dietary_notes', 'allergies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class HealthGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthGoal
        fields = ['id', 'primary_goal', 'target_weight_kg', 'weekly_activity_level', 
                  'additional_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# ---------------- Subscription Serializer ----------------
class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    class Meta:
        model = UserSubscription
        fields = ['plan_name', 'start_date', 'end_date', 'active', 'is_trial']

# ---------------- Complete User Profile ----------------
class UserProfileSerializer(serializers.ModelSerializer):
    dietary_profile = DietaryProfileSerializer(read_only=True)
    health_goal = HealthGoalSerializer(read_only=True)
    allergies = AllergyIntoleranceSerializer(many=True, read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'date_joined', 'last_login', 'dietary_profile', 'health_goal', 'allergies', 'subscription']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']