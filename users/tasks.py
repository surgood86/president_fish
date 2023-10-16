import requests
from celery import shared_task
from django.conf import settings


@shared_task
def send_sms_to(phone_number: str, code: str) -> bool:
    phone_number = '7' + phone_number
    r = requests.get(f'https://sms.ru/sms/send?api_id={settings.SMS_RU_API_ID}&to={phone_number}&msg={code}&json=1')
    if r.json().get('status_code') == 100:
        return True
    else:
        return False
