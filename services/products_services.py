from typing import Union, Optional
from uuid import UUID
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, Page
from django.http import HttpResponseRedirect, JsonResponse, HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import QuerySet
from .filters_exception_vars import PROPERTIES_EXCEPTION_DICT

from products.models import Product
from products.tasks import send_mail_to


def handle_sidebar_filters_and_return_json_response(context: dict, request_filter_param_value: dict,
                                                    filter_btn_id: str) -> JsonResponse:
    """Обрабатывает фильтры и возвращает JsonResponse с ответным queryset, и id кнопки, для изменения
    значения value"""

    if 'cancel' not in request_filter_param_value:
        new_filter_param = request_filter_param_value + 'cancel'
    else:
        new_filter_param = request_filter_param_value[:-6]

    response = render_to_string('products/products_cards.html', context)
    return JsonResponse(
        {'result': response, 'filter_btn_id': '#' + filter_btn_id, 'new_filter_param': new_filter_param})


def handle_top_filter_param_and_return_json_response(context: dict, top_param_filtered_dict: dict) -> JsonResponse:
    """Обрабатывает top_filter_param и возвращает JsonResponse"""

    top_filter_btn_id = top_param_filtered_dict['btn_id']
    top_filter_change_val = top_param_filtered_dict['change_val']
    response = render_to_string('products/products_cards.html', context)
    return JsonResponse({'result': response, 'change_val': top_filter_change_val, 'btn_id': top_filter_btn_id})


def handle_page_param_and_return_json_response(request_page: str, queryset: QuerySet, objects_num: int,
                                               context: dict) -> JsonResponse:
    """Обрабатывает page параметр в запросе и возвращает JsonResponse"""

    page_object = get_products_from_page(request_page, queryset, objects_num)
    next_page = str(int(request_page) + 1)
    context['products'] = page_object
    response_page = render_to_string('products/products_cards.html', context)
    return JsonResponse({'result': response_page, 'next_page': next_page})


def handle_order_param_and_return_json_response(request: HttpRequest,
                                                product_or_queryset: Union[Product, QuerySet]) -> JsonResponse:
    """Обрабатывает POST запрос, отправляет сообщение на почту, и возвращает json ответ
    об успехе или провале отправки сообщения"""

    date_and_time = request.POST.get('date_and_time', 'СРОЧНО!!!')
    notes = request.POST.get('notes', 'Без примечании!')
    phone_number = request.POST.get('phone_number', None)
    first_name = ''
    last_name = ''
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        if not phone_number:
            phone_number = request.user.phone_number
    if not phone_number:
        return JsonResponse({'error': 'Введите номер телефона.'})

    products_titles = ''
    if type(product_or_queryset) is Product:
        products_titles = product_or_queryset.title
    elif type(product_or_queryset) is QuerySet:
        for query in product_or_queryset:
            products_titles += query.title + ', '

    if not products_titles:
        return JsonResponse({'error': 'Укажите товары для заказа'})

    send_mail_status = send_mail_to(date_and_time, products_titles, phone_number, first_name, last_name, notes)
    if send_mail_status:
        return JsonResponse({'result': 'Благодарим за заказ, ждите звонка'})
    else:
        return JsonResponse({'error': 'Что то пошло не так'})


def handle_basket_button_and_return_json_response(request: HttpRequest) -> Optional[JsonResponse]:
    """Если параметры запроса верны, то возвращает JsonResponse, иначе None"""
    product_pk = request.POST.get('product_pk')
    user_pk = request.POST.get('user_pk')
    basket_query = request.POST.get('basket')
    if product_pk and user_pk and basket_query:
        returned_data = add_or_remove_object_from_basket_and_return_dict_for_replace_btn_text(product_pk, user_pk)
        return JsonResponse(returned_data)


def redirect_to_search(request_q: str) -> HttpResponseRedirect:
    """Обрабатывает параметр и возвращает HttpResponseRedirect, перенаправляет
    пользователя на страницу поиска"""
    url = reverse('search_list', kwargs={'q': request_q})
    return HttpResponseRedirect(url)


def get_products_from_page(request_page: Union[int, str], queryset: QuerySet, objects_num: int) -> Optional[Page]:
    """Возвращает объект Page нужной страницы если на странице есть объекты, иначе None"""

    paginator = Paginator(queryset, objects_num)
    try:
        products = paginator.page(int(request_page))
    except EmptyPage:
        products = None
    return products


def get_eng_translated_text(text: str) -> str:
    """Переводит русские буквы на английские, и заменяет спец симовлы,
    для использования как названия кнопок, или других объектов"""

    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    tr_text = text.translate(tr)
    tr_text = tr_text.replace('(', '')
    tr_text = tr_text.replace(')', '')
    tr_text = tr_text.replace(',', '_')
    tr_text = tr_text.replace(' ', '_')
    tr_text = tr_text.replace('/', '_')
    tr_text = tr_text.replace('\\', '_')
    tr_text = tr_text.replace('"', '_')

    return tr_text


def get_filters_list_for_queryset_by_properties(queryset: QuerySet) -> list:
    """Возвращает list с названиями свойств товара как title, eng_title для названия кнопок
    со списком возможных свойств в виде списка как texts.
    """

    # Инициализация переменных
    # хранит упорядоченный список названий свойств в том порядке, в котором они появляются.
    # Это полезно, например, для отображения свойств в пользовательском интерфейсе.

    titles = ['Производители']  # заголовки для кнопок
    all_products_property = [set()]  # множества уникальных свойств
    eng_titles = ['Manufacturers']  # заголовки для кнопок на английском
    all_filter_button_id = [[]]  # id для каждой кнопки фильтра
    # используется для быстрого поиска индекса, соответствующего определенному свойству.
    # Это ускоряет добавление новых элементов в all_products_property и all_filter_button_id
    all_title_to_index = {'Производители': 0}  # отображение заголовка свойства на его индекс в массиве

    # Итерация по каждому продукту в queryset
    for i, product in enumerate(queryset):

        # Добавление производителя
        all_products_property[0].add(product.manufacturer)  # добавляем всех производителей в первое множество
        all_filter_button_id[0].append(eng_titles[0] + str(i))  # формирование id кнопки (имя на английском + индекс)

        # Получение списка исключений для категории
        exceptions = set(PROPERTIES_EXCEPTION_DICT.get(product.category.title, []))  # получаем исключения для категории

        # Итерация по свойствам продукта
        for product_property in product.productproperties_set.all():
            eng_title = get_eng_translated_text(product_property.title)  # переводим заголовок свойства на английский

            # Пропуск свойств из списка исключений
            if product_property.title in exceptions:
                continue

            # Добавление или обновление свойства
            if product_property.title in all_title_to_index:  # если свойство уже существует
                index = all_title_to_index[product_property.title]  # получаем его индекс
                all_products_property[index].add(product_property.text)  # добавляем новое значение в множество
                all_filter_button_id[index].append(eng_title + str(i))  # добавляем id для новой кнопки
            else:  # если свойство новое
                titles.append(product_property.title)  # добавляем новый заголовок
                all_products_property.append({product_property.text})  # добавляем новое множество для свойств
                eng_titles.append(eng_title)  # добавляем новый английский заголовок
                all_filter_button_id.append([eng_title + str(i)])  # добавляем новый id для кнопки
                all_title_to_index[product_property.title] = len(titles) - 1  # обновляем индекс в отображении

    # Сборка итогового списка фильтров
    filter_info = list(zip(titles, eng_titles,
                           [list(zip(values, ids)) for values, ids in zip(all_products_property, all_filter_button_id)]))

    return filter_info  # возвращаем собранный список фильтров



def get_filtered_queryset_by_properties_or_manufacturer(filter_param_name: Union[str, None],
                                                        filter_param_value: Union[str, None],
                                                        queryset: QuerySet) -> QuerySet:
    """Фильтрует queryset по переданным фильтрам, и возвращает queryset, если есть объекты
    соответствующие фильтрам, иначе возвращает пустой queryset"""

    if not filter_param_name or not filter_param_value:
        return queryset

    if filter_param_name == 'Производители':
        return queryset.filter(manufacturer=filter_param_value)

    # Фильтрация продуктов по свойствам с использованием подзапросов
    return queryset.filter(
        productproperties__title=filter_param_name,
        productproperties__text=filter_param_value
    )



def get_sorted_queryset_and_update_top_filter_btn(
        top_filter_param: str, queryset: QuerySet) -> dict:
    """Возвращает dict с отсортированным по цене или названию queryset, и новое значение для
    кнопки сортировки price или title"""

    if not top_filter_param:
        return {'queryset': queryset}

    filter_params = {
        'price_asc': {'order_by': 'price', 'change_val': 'price_desc', 'btn_id': '#priceFilter'},
        'price_desc': {'order_by': '-price', 'change_val': 'price_asc', 'btn_id': '#priceFilter'},
        'title_asc': {'order_by': 'title', 'change_val': 'title_desc', 'btn_id': '#nameFilter'},
        'title_desc': {'order_by': '-title', 'change_val': 'title_asc', 'btn_id': '#nameFilter'},
    }

    if top_filter_param not in filter_params:
        raise ValueError(f"Неверный параметр: {top_filter_param}")

    param = filter_params[top_filter_param]
    queryset = queryset.order_by(param['order_by'])

    top_param_filtered_dict = {
        'queryset': queryset,
        'change_val': param['change_val'],
        'btn_id': param['btn_id'],
    }

    return top_param_filtered_dict


def add_or_remove_object_from_basket_and_return_dict_for_replace_btn_text(product_pk: str,
                                                                          user_pk: UUID) -> Optional[dict]:
    """Добавляет в корзину пользователя товар, если его там нет, иначе удаляет
    и возвращает текст для замены на кнопке"""
    returned_data = dict()
    if get_user_model().objects.filter(pk=user_pk):
        user = get_user_model().objects.get(pk=user_pk)
    else:
        return None
    product = Product.objects.get(pk=product_pk)
    if product.users.filter(pk=user_pk):
        product.users.remove(user)
        returned_data['result'] = 'Добавить в корзину'
    else:
        product.users.add(user)
        returned_data['result'] = 'Удалить из корзины'
    product.save()
    returned_data['btn_id'] = f'#{product.eng_title}'
    return returned_data


def add_objects_in_queryset_is_in_basket_attr(queryset: QuerySet, user_pk: UUID) -> None:
    """Добавляет в объекты queryset поле is_in_basket для определения находится ли
    объект в корзине пользователя или нет"""
    for query in queryset:
        if query.users.filter(pk=user_pk):
            query.is_in_basket = True
        else:
            query.is_in_basket = False


def get_is_in_basket_attr_for_single_object(user_pk: UUID, product_pk: str) -> bool:
    """Возвращает атрибут показывающий, находится ли product в корзине пользователя
    или нет"""

    product = Product.objects.get(pk=product_pk)
    if product.users.filter(pk=user_pk):
        return True
    else:
        return False
