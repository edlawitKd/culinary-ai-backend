from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Recipe, FavoriteRecipe
from .serializers import RecipeSerializer
from pantry.models import PantryItem

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related('ingredients', 'steps', 'favorite_recipes').order_by('-created_at')
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'favorite', 'what_can_i_cook', 'clean_up_mode']:
            return [IsAuthenticated()]
        return [AllowAny()]

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

        suggested = []
        for recipe in Recipe.objects.all():
            ingredients = {ing.name.lower() for ing in recipe.ingredients.all()}
            missing = ingredients - pantry_names
            available = ingredients & pantry_names
            suggested.append({
                "recipe": recipe,
                "available": list(available),
                "missing": list(missing),
                "score": len(available) - len(missing)
            })

        suggested.sort(key=lambda x: x['score'], reverse=True)
        results = []
        for s in suggested:
            serializer = RecipeSerializer(s['recipe'], context={'request': request})
            data = serializer.data
            data['available_ingredients'] = s['available']
            data['missing_ingredients'] = s['missing']
            results.append(data)
        return Response(results)

    @action(detail=False, methods=['get'])
    def clean_up_mode(self, request):
        user = request.user
        pantry_items = PantryItem.objects.filter(user=user)
        soon_expiring = {item.name.lower(): item for item in pantry_items if item.expiry_date}
        
        suggestions = []
        for recipe in Recipe.objects.all():
            ingredients = {ing.name.lower(): ing for ing in recipe.ingredients.all()}
            score = 0
            for name in ingredients:
                if name in soon_expiring:
                    days_until_expiry = (soon_expiring[name].expiry_date - soon_expiring[name].created_at.date()).days
                    score += max(0, 7 - days_until_expiry)
            suggestions.append({"recipe": recipe, "score": score})
        
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        results = [RecipeSerializer(s['recipe'], context={'request': request}).data for s in suggestions]
        return Response(results)