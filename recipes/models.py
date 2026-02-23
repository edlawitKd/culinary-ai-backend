from django.db import models
from django.conf import settings

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
        ("dessert", "Dessert"),
        ("other", "Other"),
    ]
    
    name = models.CharField(max_length=150, default="Unnamed Recipe")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recipes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    servings = models.PositiveIntegerField(default=1)
    allergens = models.JSONField(default=list, blank=True)  # e.g., ["nuts", "gluten"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField()  # numeric part
    unit = models.CharField(max_length=50, default="")  # e.g., "tsp", "cups", "pcs"

    # Nutrition per unit 
    calories_per_unit = models.FloatField(default=0)
    protein_per_unit = models.FloatField(default=0)
    carbs_per_unit = models.FloatField(default=0)
    fat_per_unit = models.FloatField(default=0)

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}".strip()


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="steps", on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)  # optional
    instruction = models.TextField(blank=True, null=True)  # optional

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} for {self.recipe.name}"


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorite_recipes")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe")  # prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.name}"


class RecipeSubstitution(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="substitutions"
    )
    original_ingredient = models.CharField(max_length=100)
    substitute_ingredient = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.substitute_ingredient} for {self.original_ingredient} in {self.recipe.name}"