from django.views import generic
from django.contrib.auth import views, get_user_model, login, authenticate
from django.http import JsonResponse
from django.conf import settings

from services import auth_services

User = get_user_model()


class SignUpView(generic.TemplateView):
    """View для обработки данных пользователя для регистрации"""
    template_name = 'users/signup.html'

    def post(self, request, *args, **kwargs):
        json_response = auth_services.handle_user_data_and_get_json_response(request)
        return json_response


class SignInView(views.LoginView):
    """View для обработки данных пользователя для входа"""
    template_name = 'users/signin.html'

    def post(self, request, *args, **kwargs):
        cleaned_phone_number = auth_services.get_cleaned_phone_number(request.POST.get('phone_number', None))
        password = request.POST.get('password', None)
        user = authenticate(phone_number=cleaned_phone_number, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success_url': settings.LOGIN_REDIRECT_URL})
        else:
            if User.objects.filter(phone_number=cleaned_phone_number):
                user = User.objects.get(phone_number=cleaned_phone_number)
                if not user.is_active:
                    return JsonResponse({'error': 'Этот номер не подтвержден, для входа подтвердите номер'})
                else:
                    return JsonResponse({'error': 'Номер и пароль не совпадают'})
            else:
                return JsonResponse({'error': 'Пользователя с таким номером не существует'})


class ConfirmCodeView(generic.View):
    """View для обработки введенного кода для активации пользователя или возврата ошибки"""

    def post(self, request, *args, **kwargs):
        purpose = request.POST.get('purpose')
        if purpose == 'password_reset':
            json_response = auth_services.handle_code_for_password_reset(request)
        else:
            json_response = auth_services.handle_code_for_user_registration(request)
        return json_response


class PasswordResetView(generic.TemplateView):
    """View для обработки восстановления пароля пользователя"""
    template_name = 'users/input_number.html'

    def post(self, request, *args, **kwargs):
        password1 = request.POST.get('password1')
        if password1:
            json_response = auth_services.handle_passwords_in_request(request)
        else:
            json_response = auth_services.handle_password_reset_request_with_phone_number(request)
        return json_response
