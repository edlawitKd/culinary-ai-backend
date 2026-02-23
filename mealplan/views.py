from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MealPlan, DailyMeal, CookingEvent
from .serializers import MealPlanSerializer, DailyMealSerializer, CookingEventSerializer
from recipes.models import Recipe
from django.utils import timezone
from datetime import timedelta, date

class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user).order_by('-week_start')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ---------------- Generate Weekly Meal Plan ----------------
    @action(detail=False, methods=['post'])
    def generate_week(self, request):
        user = request.user
        today = date.today()
        monday = today - timedelta(days=today.weekday())  # start of the week

        # Remove existing plan for this week
        MealPlan.objects.filter(user=user, week_start=monday).delete()
        meal_plan = MealPlan.objects.create(user=user, week_start=monday)

        # User data
        pantry_items = {item.name.lower() for item in user.pantry_items.all()}
        allergies = {a.allergy_type.lower() for a in user.allergies.all()}
        dietary_pref = getattr(user, 'dietary_profile', None)

        # Filter recipes
        recipes = []
        for recipe in Recipe.objects.all().prefetch_related('ingredients'):
            ing_names = {ing.name.lower() for ing in recipe.ingredients.all()}
            if ing_names & allergies:
                continue
            if dietary_pref and dietary_pref.dietary_preference != 'none':
                recipe_tags = {tag.lower() for tag in recipe.allergens}
                if dietary_pref.dietary_preference.lower() not in recipe_tags:
                    continue
            recipes.append(recipe)

        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        for i, day in enumerate(days):
            if recipes:
                recipe = recipes[i % len(recipes)]
                DailyMeal.objects.create(meal_plan=meal_plan, day=day, recipe=recipe)

        serializer = MealPlanSerializer(meal_plan, context={'request': request})
        return Response(serializer.data)

    # ---------------- Add Recipe to a Day ----------------
    @action(detail=True, methods=['post'])
    def add_daily_meal(self, request, pk=None):
        meal_plan = self.get_object()
        day = request.data.get('day')
        recipe_id = request.data.get('recipe')
        servings = request.data.get('servings', 1)

        if not day or not recipe_id:
            return Response({"error": "day and recipe are required"}, status=400)

        daily_meal, created = DailyMeal.objects.update_or_create(
            meal_plan=meal_plan,
            day=day,
            defaults={"recipe_id": recipe_id, "servings": servings}
        )
        serializer = DailyMealSerializer(daily_meal)
        return Response(serializer.data)

    # ---------------- Cook Daily Meal ----------------
    @action(detail=True, methods=['post'])
    def cook(self, request, pk=None):
        meal_plan = self.get_object()
        day = request.data.get('day')
        try:
            daily_meal = meal_plan.daily_meals.get(day=day)
        except DailyMeal.DoesNotExist:
            return Response({"error": "No meal for this day"}, status=404)

        cooked_event, created = CookingEvent.objects.get_or_create(daily_meal=daily_meal)
        serializer = CookingEventSerializer(cooked_event)
        return Response(serializer.data)