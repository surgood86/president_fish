import random
from typing import Union
from django.utils.safestring import SafeString
from django.template.loader import render_to_string
from django.http.response import JsonResponse
from django.http.request import HttpRequest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.conf import settings
from django.contrib.auth import login

from users import tasks

User = get_user_model()


def get_cleaned_phone_number(phone_number: Union[str, None]) -> str:
    """Очищает введенные данные от лишних символов и возвращает правильный номер"""

    if phone_number is None:
        return ''

    phone_number = ''.join([i for i in phone_number if i.isdigit()])
    if len(phone_number) > 10:
        phone_number = phone_number[-10:]
    return phone_number


def check_passwords(password1: str, password2: str, user) -> str:
    """Проверяет пароли на правильность"""
    if not password1:
        return 'Введите пароль'
    if not password2:
        return 'Подтвердите пароль'
    if not password1 == password2:
        return 'Пароли не совпадают'
    try:
        password_validation.validate_password(password1, user)
    except ValidationError:
        return get_password_validators_help_texts()


def get_password_validators_help_texts() -> str:
    """Возвращает строку с правилами для ввода пароля"""
    return 'Ваш пароль не может быть похожим на ваши данные.\n' \
           'Ваш пароль должен содержать не менее 8 символов.\n' \
           'Ваш пароль не может быть распространенным.\n' \
           'Ваш пароль не может состоять только из цифр.'


def get_rendered_html_to_confirm_code(phone_number: str, purpose: str) -> SafeString:
    """Возвращет html с формой для ввода кода из смс"""
    response = render_to_string('users/form_for_code.html', context={'phone_number': phone_number, 'purpose': purpose})
    return response


def handle_user_data_and_get_json_response(request: HttpRequest) -> JsonResponse:
    """Обрабатывает post запрос с данными пользоветля для регистрации, при удаче возвращает html форму
    для ввода кода из смс, иначе возвращает json ответ с текстом ошибки"""
    phone_number = request.POST.get('phone_number')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    if not phone_number:
        return JsonResponse({'error': 'Введите пожалуйста номер телефона корректно.'})
    if first_name:
        for i in first_name:
            if not i.isalpha():
                return JsonResponse({'error': 'Имя может состоять только из букв'})
    if last_name:
        for i in last_name:
            if not i.isalpha():
                return JsonResponse({'error': 'Фамилия может состоять только из букв'})

    cleaned_phone_number = get_cleaned_phone_number(request.POST.get('phone_number'))
    if User.objects.filter(phone_number=cleaned_phone_number):
        return JsonResponse({'error': 'Пользователь с таким номером уже существует.'})

    user = User(cleaned_phone_number, first_name, last_name)
    error_in_passwords = check_passwords(password1, password2, user)
    if error_in_passwords:
        return JsonResponse({'error': error_in_passwords})
    user = User.objects.create_user(phone_number=cleaned_phone_number, password=password1, code=get_random_code(),
                                    first_name=first_name, last_name=last_name)
    response = tasks.send_sms_to(cleaned_phone_number, user.code)
    if response:
        return JsonResponse({'success': get_rendered_html_to_confirm_code(cleaned_phone_number, 'registration')})
    else:
        return JsonResponse({'error': 'Что-то пошло не так, повторите попытку позже'})


def get_random_code(length: int = 4) -> str:
    """Принимает int, и в зависмости от числа возвращает рандомно сгенерированный str со случайными числа
    длиною в int который был введен"""
    start_num = 10**length
    end_num = 10**(length+1) - 1
    return str(random.randint(start_num, end_num))


def confirm_code(phone_number: str, code: str) -> Union[str, bool]:
    """Подтверждает корректность кода, возвращает bool в зависимости от коррестности кода, или возвращает
    строку again, если надо заново отправить код"""
    if code == 'again':
        return 'again'
    if User.objects.filter(phone_number=phone_number):
        user = User.objects.get(phone_number=phone_number)
        if code == user.code:
            return True
        else:
            return False
    else:
        return False


def handle_code_for_user_registration(request: HttpRequest) -> JsonResponse:
    """Обрабатывает post запрос с данными о коде, при успехе меняет статус пользователя на актинвый и возвращает
    ссылку на которую надо перенаправить пользователя, иначе возвращает json ответ об ошибке"""
    code = request.POST.get('code')
    phone_number = request.POST.get('phone_number')
    if not code:
        return JsonResponse({'error': 'Введите код из смс пожалуйста'})
    is_code = confirm_code(phone_number, code)
    if is_code == 'again':
        if User.objects.filter(phone_number=phone_number):
            user = User.objects.get(phone_number=phone_number)
            response = tasks.send_sms_to(phone_number, user.code)
            if response:
                return JsonResponse({'success': 'Код повторно отправлен на ваш номер'})
            else:
                return JsonResponse({'error': 'Что-то пошло не так, повторите попытку позже'})
    else:
        if User.objects.filter(phone_number=phone_number):
            user = User.objects.get(phone_number=phone_number)
            if is_code:
                user.is_active = True
                user.code = None
                user.save()
                login(request, user)
                return JsonResponse({'success_url': settings.LOGIN_REDIRECT_URL})
            else:
                return JsonResponse({'error': 'Код введен неверно'})


def handle_password_reset_request_with_phone_number(request: HttpRequest) -> JsonResponse:
    """Обрабатывает запрос на восстановление пароля, и возвращает json ответ"""
    phone_number = get_cleaned_phone_number(request.POST.get('phone_number'))
    if not User.objects.filter(phone_number=phone_number):
        return JsonResponse({'error': "Пользователя с таким номером не существует"})
    user = User.objects.get(phone_number=phone_number)
    user.code = get_random_code()
    user.save()
    response = tasks.send_sms_to(phone_number, user.code)
    if response:
        return JsonResponse({'success': get_rendered_html_to_confirm_code(phone_number, 'password_reset')})
    else:
        return JsonResponse({'error': 'Что-то пошло не так, попробуйте позже'})


def handle_code_for_password_reset(request: HttpRequest) -> JsonResponse:
    """Обрабатывает введеныый код в запросе и возвращает json ответ"""
    code = request.POST.get('code')
    phone_number = request.POST.get('phone_number')
    is_code = confirm_code(phone_number, code)
    if User.objects.filter(phone_number=phone_number):
        user = User.objects.get(phone_number=phone_number)
    else:
        return JsonResponse({'error': 'Невозможно найти пользователя с таким номером'})
    if is_code == 'again':
        tasks.send_sms_to(phone_number, code)
        return JsonResponse({'success': 'Код заново отправлен на ваш номер'})
    else:
        if is_code:
            user.code = None
            user.save()
            return JsonResponse({'success': get_rendered_form_for_password_inputting(phone_number)})
        else:
            return JsonResponse({'error': 'Введен неверный код'})


def get_rendered_form_for_password_inputting(phone_number: str) -> SafeString:
    """Возвращает отрендеренную форму для ввода пароля"""
    response = render_to_string('users/create_new_password.html', context={'phone_number': phone_number})
    return response


def handle_passwords_in_request(request: HttpRequest) -> JsonResponse:
    """Обрабатывает запрос с новыми паролями пользователя и возвращает json ответ"""
    phone_number = request.POST.get('phone_number')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    if not phone_number:
        return JsonResponse({'error': 'Не введен номер телефона'})
    if User.objects.filter(phone_number=phone_number):
        user = User.objects.get(phone_number=phone_number)
    else:
        return JsonResponse({'error': 'Пользователя с таким номером не существует'})
    error_in_passwords = check_passwords(password1, password2, user)
    if error_in_passwords:
        return JsonResponse({'error': error_in_passwords})
    else:
        user.is_active = True
        user.set_password(password1)
        user.save()
        login(request, user)
        return JsonResponse({'success_url': settings.LOGIN_REDIRECT_URL})
