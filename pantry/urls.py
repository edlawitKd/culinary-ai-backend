from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_item),
    path("list/", views.list_items),
    path("update/<int:pk>/", views.update_item),
    path("delete/<int:pk>/", views.delete_item),
    path("expiring/", views.expiring_items),
    path("cleanup-suggestions/", views.cleanup_suggestions),
]