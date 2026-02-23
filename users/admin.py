from django.contrib import admin
from .models import User, DietaryProfile, HealthGoal, AllergyIntolerance
# Register your models here.

admin.site.register(User)
admin.site.register(DietaryProfile)
admin.site.register(HealthGoal) 