from rest_framework import serializers
from .models import MealPlan, DailyMeal, CookingEvent
from recipes.serializers import RecipeSerializer

class DailyMealSerializer(serializers.ModelSerializer):
    recipe_details = RecipeSerializer(source='recipe', read_only=True)

    class Meta:
        model = DailyMeal
        fields = ['id', 'day', 'recipe', 'recipe_details', 'servings']


class MealPlanSerializer(serializers.ModelSerializer):
    daily_meals = DailyMealSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = ['id', 'week_start', 'daily_meals', 'created_at', 'updated_at']


class CookingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingEvent
        fields = ['id', 'daily_meal', 'cooked_at']
        read_only_fields = ['cooked_at']