from django.core import exceptions
from django.views import generic

from services import products_services

from .models import Category

from products.views import ProductsListView


class HomeView(generic.ListView):
    """Отображает главную страницу, и все категории на нем"""

    model = Category
    context_object_name = 'categories_products'
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        q = self.request.GET.get('q', None)
        if q:
            return products_services.redirect_to_search(q)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all()

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)

        data['categories'] = Category.objects.all()

        return data


class CategoryDetailView(ProductsListView):
    """Отображает список товаров из запрошенной категории, наследуется от ProductsListView"""

    def get_object(self, queryset=None):
        if Category.objects.filter(pk=self.kwargs['pk']):
            return Category.objects.get(pk=self.kwargs['pk'])
        else:
            raise exceptions.ObjectDoesNotExist

    def get_queryset(self):
        category = self.get_object()
        queryset = category.product_set.all()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)

        data['page_title'] = self.get_object().title

        return data
