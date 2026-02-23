from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import date, timedelta
from rest_framework.permissions import IsAuthenticated
from .models import PantryItem
from .serializers import PantryItemSerializer


# ---------------- ADD ITEM ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_item(request):
    serializer = PantryItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- LIST ITEMS ----------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_items(request):
    items = PantryItem.objects.filter(user=request.user).order_by("-created_at")
    serializer = PantryItemSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------- UPDATE ITEM ----------------
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_item(request, pk):
    try:item = PantryItem.objects.get(id=pk, user=request.user)
    except PantryItem.DoesNotExist:
        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PantryItemSerializer(
        item,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- DELETE ITEM ----------------
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_item(request, pk):
    try:
        item = PantryItem.objects.get(id=pk, user=request.user)
        item.delete()
        return Response(
            {"message": "Deleted successfully"},
            status=status.HTTP_200_OK
        )
    except PantryItem.DoesNotExist:
        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND
        )


# ---------------- EXPIRING ITEMS ----------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expiring_items(request):
    today = date.today()
    soon = today + timedelta(days=3)

    items = PantryItem.objects.filter(user=request.user, expiry_date__range=(today, soon))

    serializer = PantryItemSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------- CLEANUP SUGGESTIONS ----------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cleanup_suggestions(request):
    today = date.today()
    soon = today + timedelta(days=3)

    items = PantryItem.objects.filter(user=request.user)
    
    expired = items.filter(expiry_date__lt=today)
    expiring = items.filter(expiry_date__range=(today, soon))
    low_stock = items.filter(quantity__lte=1)

    return Response({
        "expired": PantryItemSerializer(expired, many=True).data,
        "expiring_soon": PantryItemSerializer(expiring, many=True).data,
        "low_stock": PantryItemSerializer(low_stock, many=True).data
    }, status=status.HTTP_200_OK)