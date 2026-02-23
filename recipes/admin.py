from django.contrib import admin
from .models import Recipe, Ingredient, Step, FavoriteRecipe, RecipeSubstitution

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1

class StepInline(admin.TabularInline):
    model = Step
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at', 'created_by')
    inlines = [IngredientInline, StepInline]