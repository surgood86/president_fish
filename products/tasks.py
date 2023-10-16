from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_mail_to(date_and_time: str, products_titles: str, user_phone_number: str, user_first_name: str = 'Не указан',
                 user_last_name: str = 'Не указан', notes: str = 'Без примечании') -> bool:
    """Отправляет на почту время ожидания звонка, название товара, номер пользователя, примечания и
    возвращает bool"""

    if not products_titles:
        return False

    mail_to_send = f'Товар: {products_titles}\n' \
                   f'Номер: {user_phone_number}\n' \
                   f'Имя: {user_first_name}\n' \
                   f'Фамилия: {user_last_name}\n' \
                   f'Примечания {notes}'

    mail = send_mail(date_and_time, mail_to_send, settings.EMAIL_HOST_USER, [settings.EMAIL_SEND_MAIL_TO_USER],
                     fail_silently=False)
    if mail == 1:
        task_completed = True
    else:
        task_completed = False
    return task_completed
