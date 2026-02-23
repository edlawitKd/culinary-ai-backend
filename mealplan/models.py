from django.db import models
from django.conf import settings
from recipes.models import Recipe
from pantry.models import PantryItem
from django.utils import timezone
from datetime import timedelta

# ---------------- Weekly Meal Plan ----------------
class MealPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meal_plans")
    week_start = models.DateField()  # Monday of the week
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "week_start"]

    def __str__(self):
        return f"{self.user.username}'s Meal Plan starting {self.week_start}"


# ---------------- Daily Meal ----------------
class DailyMeal(models.Model):
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="daily_meals")
    day = models.CharField(max_length=10, choices=DAYS)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    servings = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ["meal_plan", "day"]

    def __str__(self):
        return f"{self.meal_plan.user.username} - {self.day}: {self.recipe.name if self.recipe else 'No Recipe'}"


# ---------------- Cooking Event ----------------
class CookingEvent(models.Model):
    daily_meal = models.OneToOneField(DailyMeal, on_delete=models.CASCADE, related_name="cooked")
    cooked_at = models.DateTimeField(auto_now_add=True)

    def deduct_ingredients(self):
        pantry_items = {item.name.lower(): item for item in self.daily_meal.recipe.created_by.pantry_items.all()}
        for ing in self.daily_meal.recipe.ingredients.all():
            qty_needed = ing.quantity * self.daily_meal.servings
            pantry_item = pantry_items.get(ing.name.lower())
            if pantry_item:
                pantry_item.quantity = max(0, pantry_item.quantity - qty_needed)
                pantry_item.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.deduct_ingredients()