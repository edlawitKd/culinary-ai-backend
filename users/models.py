from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

# ---------------- User Manager ----------------
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

# ---------------- User Model ----------------
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

# ---------------- Dietary Profile ----------------
class DietaryProfile(models.Model):
    DIETARY_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Keto'),
        ('paleo', 'Paleo'),
        ('gluten_free', 'Gluten-Free'),
        ('dairy_free', 'Dairy-Free'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
        ('none', 'No Restrictions'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dietary_profile')
    dietary_preference = models.CharField(max_length=50, choices=DIETARY_CHOICES, default='none')
    custom_dietary_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Dietary Profile"

# ---------------- Health Goal ----------------
class HealthGoal(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Build Muscle'),
        ('improve_energy', 'Improve Energy'),
        ('better_sleep', 'Better Sleep'),
        ('improve_digestion', 'Improve Digestion'),
        ('general_health', 'General Health Improvement'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_goal')
    primary_goal = models.CharField(max_length=50, choices=GOAL_CHOICES, default='general_health')
    target_weight_kg = models.FloatField(null=True, blank=True)
    weekly_activity_level = models.CharField(max_length=50, choices=[
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extra_active', 'Extra Active'),
    ], default='moderately_active')
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Health Goal"

# ---------------- Allergies ----------------
class AllergyIntolerance(models.Model):
    ALLERGY_TYPES = [
        ('dairy', 'Dairy'),
        ('eggs', 'Eggs'),
        ('fish', 'Fish'),
        ('shellfish', 'Shellfish'),
        ('tree_nuts', 'Tree Nuts'),
        ('peanuts', 'Peanuts'),
        ('wheat', 'Wheat'),
        ('soy', 'Soy'),
        ('sesame', 'Sesame'),
        ('gluten', 'Gluten'),
        ('corn', 'Corn'),
        ('sulfites', 'Sulfites'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allergies')
    allergy_type = models.CharField(max_length=50, choices=ALLERGY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    specific_notes = models.TextField(blank=True, help_text="Any specific details about this allergy")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'allergy_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_allergy_type_display()}"

# ---------------- Subscription ----------------
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    duration_days = models.IntegerField(default=30)  # e.g., 30-day, 90-day
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_subscription")  # <--- updated
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_trial and not self.end_date:
            self.end_date = timezone.now() + timedelta(days=7)  # 7-day trial
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'Trial'}"