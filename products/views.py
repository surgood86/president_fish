from services import products_services
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import exceptions
from .models import Product
from categories.models import Category

User = get_user_model()


class ProductsListView(generic.ListView):
    """Отображает отображает весь список товаров, и обрабатывает параметры запроса, является
    родительским классом для остальных классов"""
    template_name = 'products/products_list.html'
    model = Product
    context_object_name = 'products'
    pages_paginate = 6

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        context = self.get_context_data(**kwargs)
        user = request.user

        request_q = request.GET.get('q')
        request_page = request.GET.get('page')
        request_filter_btn_id = request.GET.get('filter_btn_id')
        request_top_filter_param = request.GET.get('top_filter_param')
        request_filter_param_name = request.GET.get('filter_param_name')
        request_filter_param_value = request.GET.get('filter_param_value')

        if request_q:
            return products_services.redirect_to_search(request_q)

        if request_filter_param_name and request_filter_param_value:
            queryset = products_services.get_filtered_queryset_by_properties_or_manufacturer(
                request_filter_param_name, request_filter_param_value, queryset
            )

        if request_top_filter_param:
            top_param_filtered_dict = products_services.get_sorted_queryset_and_update_top_filter_btn(
                request_top_filter_param, queryset
            )
            queryset = top_param_filtered_dict['queryset']

        products_services.add_objects_in_queryset_is_in_basket_attr(queryset, user.pk)

        page_object = products_services.get_products_from_page(
            1 if not request_page else int(request_page), queryset, self.pages_paginate
        )
        context['products'] = page_object

        if request_page:
            return products_services.handle_page_param_and_return_json_response(
                request_page, queryset, self.pages_paginate, context
            )

        if request_top_filter_param:
            return products_services.handle_top_filter_param_and_return_json_response(
                context, top_param_filtered_dict
            )

        if request_filter_param_name and request_filter_param_value:
            return products_services.handle_sidebar_filters_and_return_json_response(
                context, request_filter_param_value, request_filter_btn_id
            )

        response = render(request, self.template_name, context)
        return HttpResponse(response)

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = kwargs.pop('object_list', None)
        if not queryset:
            self.object_list = self.get_queryset()
        data = super().get_context_data(**kwargs)

        data['categories'] = Category.objects.all()
        data['filters'] = products_services.get_filters_list_for_queryset_by_properties(self.get_queryset())
        data['page_title'] = 'Товары'

        return data

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def post(self, *args, **kwargs):
        basket = self.request.POST.get('basket', None)
        if basket:
            return products_services.handle_basket_button_and_return_json_response(self.request)


class BasketView(LoginRequiredMixin, ProductsListView):
    """Отображает список из корзины пользователя, наследуется от ProductsListView"""

    def get_queryset(self):
        user = self.request.user

        queryset = user.product_set.all()

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)

        data['page_title'] = 'Корзина'
        data['filters'] = ''
        data['manufacturers'] = ''
        data['basket'] = True

        return data

    def post(self, *args, **kwargs):
        order = self.request.POST.get('order', None)
        if order:
            return products_services.handle_order_param_and_return_json_response(
                self.request, self.get_queryset()
            )
        return super().post(*args, **kwargs)


class SearchListView(ProductsListView):
    """Отображает список товаров из поиска, все запросы на поиск перенаправляются на этот view,
    наследуется от ProductsListView"""

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.kwargs['q']
        queryset = queryset.filter(Q(title__icontains=q))

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['page_title'] = 'Поиск'
        return data


class ProductDetailView(generic.DetailView):
    """Отображает детальную информацию о товаре, так же обрабатывает POST запрос на заказ"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_object(self, **kwargs):
        user = self.request.user
        if Product.objects.filter(pk=self.kwargs['pk']):
            product = Product.objects.get(pk=self.kwargs['pk'])
            if user:
                product.is_in_basket = products_services.get_is_in_basket_attr_for_single_object(user.pk, product.pk)
            else:
                product.is_in_basket = False
            return product
        else:
            raise exceptions.ObjectDoesNotExist

    def get(self, request, *args, **kwargs):
        request_q = self.request.GET.get('q')
        if request_q:
            return products_services.redirect_to_search(request_q)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['five_properties'] = self.object.productproperties_set.all()[:5]
        data['categories'] = Category.objects.all()

        obj = self.get_object()
        first_image_pk = obj.productimages_set.first().pk
        remaining_images = obj.productimages_set.exclude(pk=first_image_pk)
        data['remaining_images'] = remaining_images

        return data

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        order = request.POST.get('order')
        basket = request.POST.get('basket')

        if order:
            return products_services.handle_order_param_and_return_json_response(request, product)
        elif basket:
            return products_services.handle_basket_button_and_return_json_response(self.request)
