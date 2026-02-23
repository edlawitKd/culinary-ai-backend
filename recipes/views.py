from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Recipe, FavoriteRecipe
from .serializers import RecipeSerializer
from pantry.models import PantryItem
from django.utils import timezone

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients', 'steps', 'favorite_recipes', 'substitutions'
    ).order_by('-created_at')
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'favorite', 'what_can_i_cook', 'clean_up_mode']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        fav, created = FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            fav.delete()
            return Response({"status": "removed from favorites"})
        return Response({"status": "added to favorites"})

    @action(detail=False, methods=['get'])
    def what_can_i_cook(self, request):
        user = request.user
        pantry_items = PantryItem.objects.filter(user=user)
        pantry_names = {item.name.lower() for item in pantry_items}

        # User data
        user_allergies = {a.allergy_type.lower() for a in user.allergies.all()}
        dietary_pref = getattr(user, 'dietary_profile', None)
        health_goal = getattr(user, 'health_goal', None)

        suggested = []

        for recipe in Recipe.objects.all().prefetch_related('ingredients', 'substitutions'):
            ingredient_names = {ing.name.lower() for ing in recipe.ingredients.all()}

            # Skip allergens
            if user_allergies & ingredient_names:
                continue

            # Dietary preference
            if dietary_pref and dietary_pref.dietary_preference != 'none':
                recipe_tags = {tag.lower() for tag in recipe.allergens}
                if dietary_pref.dietary_preference.lower() not in recipe_tags:
                    continue

            missing = ingredient_names - pantry_names
            available = ingredient_names & pantry_names

            # Substitutions
            substitutions_used = []
            for sub in recipe.substitutions.all():
                orig = sub.original_ingredient.lower()
                sub_name = sub.substitute_ingredient.lower()
                if orig in missing and sub_name in pantry_names:
                    missing.remove(orig)
                    available.add(sub_name)
                    substitutions_used.append(f"{orig} -> {sub_name}")

            # Nutrition totals
            total_calories = sum(ing.quantity * ing.calories_per_unit for ing in recipe.ingredients.all())
            total_protein = sum(ing.quantity * ing.protein_per_unit for ing in recipe.ingredients.all())
            total_carbs = sum(ing.quantity * ing.carbs_per_unit for ing in recipe.ingredients.all())
            total_fat = sum(ing.quantity * ing.fat_per_unit for ing in recipe.ingredients.all())

            # Health goal scoring
            health_score = 0
            if health_goal:
                if health_goal.primary_goal == 'weight_loss':
                    health_score = max(0, 100 - total_calories)
                elif health_goal.primary_goal == 'build_muscle':
                    health_score = total_protein
                elif health_goal.primary_goal == 'maintain_weight':
                    health_score = max(0, 100 - abs(total_calories - 2000))

            pantry_score = len(available) - len(missing)
            final_score = pantry_score + health_score

            suggested.append({
                "recipe": recipe,
                "available": list(available),
                "missing": list(missing),
                "substitutions_used": substitutions_used,
                "score": final_score
            })

        suggested.sort(key=lambda x: x['score'], reverse=True)

        results = []
        for s in suggested:
            serializer = RecipeSerializer(s['recipe'], context={'request': request})
            data = serializer.data
            data['available_ingredients'] = s['available']
            data['missing_ingredients'] = s['missing']
            data['substitutions_used'] = s['substitutions_used']
            data['score'] = s['score']
            results.append(data)

        return Response(results)

    @action(detail=False, methods=['get'])
    def clean_up_mode(self, request):
        user = request.user
        today = timezone.now().date()
        pantry_items = PantryItem.objects.filter(user=user)
        soon_expiring = {item.name.lower(): item.expiry_date for item in pantry_items if item.expiry_date}

        user_allergies = {a.allergy_type.lower() for a in user.allergies.all()}

        suggestions = []
        for recipe in Recipe.objects.all().prefetch_related('ingredients'):
            ingredient_names = {ing.name.lower() for ing in recipe.ingredients.all()}

            # Skip if recipe has allergens
            if user_allergies & ingredient_names:
                continue

            score = 0
            for name in ingredient_names:
                if name in soon_expiring:
                    days_until_expiry = (soon_expiring[name] - today).days
                    if days_until_expiry >= 0:
                        score += max(0, 7 - days_until_expiry)

            suggestions.append({"recipe": recipe, "score": score})

        suggestions.sort(key=lambda x: x['score'], reverse=True)
        results = [RecipeSerializer(s['recipe'], context={'request': request}).data for s in suggestions]
        return Response(results)