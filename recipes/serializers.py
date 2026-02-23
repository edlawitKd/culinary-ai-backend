from rest_framework import serializers
from .models import Recipe, Ingredient, Step, FavoriteRecipe, RecipeSubstitution

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'quantity', 'unit',
            'calories_per_unit', 'protein_per_unit', 'carbs_per_unit', 'fat_per_unit'
        ]

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'step_number', 'instruction']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    steps = StepSerializer(many=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'image', 'category', 'created_by',
            'created_at', 'servings', 'allergens', 'ingredients', 'steps', 'is_favorite'
        ]
        read_only_fields = ['created_by', 'created_at']

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorite_recipes.filter(user=user).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        steps_data = validated_data.pop('steps', [])
        user = self.context['request'].user
        validated_data.pop('created_by', None)

        recipe = Recipe.objects.create(created_by=user, **validated_data)

        for ing_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ing_data)
        for step_data in steps_data:
            Step.objects.create(recipe=recipe, **step_data)

        return recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ['id', 'user', 'recipe', 'added_at']


class RecipeSubstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeSubstitution
        fields = ['id', 'recipe', 'original_ingredient', 'substitute_ingredient']