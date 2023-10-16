from django.urls import path

from .views import ProductsListView, ProductDetailView, BasketView, SearchListView


urlpatterns = [
    path('', ProductsListView.as_view(), name='products_list'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('search/<str:q>/', SearchListView.as_view(), name='search_list'),
    path('product/<str:pk>/', ProductDetailView.as_view(), name='product_detail'),
]