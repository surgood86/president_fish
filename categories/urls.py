from django.urls import path

from .views import HomeView, CategoryDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<str:pk>/', CategoryDetailView.as_view(), name='category_detail'),
]