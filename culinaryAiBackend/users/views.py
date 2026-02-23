from rest_framework import generics ,permissions
from .models import User
from .serializers import UserSerializer

class UserListView(generics.ListCreateAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
   