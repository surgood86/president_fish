#from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем, где находится модуль Джанго и файл настроек; Должна всегда находится перед созданием экземпляров приложения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'president_fish.settings')

app = Celery('president_fish') # создаём объект и передаём ему имя
#чтобы это работало с джанго передаём django.conf и настройки settings
#namespace - при чтении из настроек ищет переменные начинающиеся на заданное имя
app.config_from_object('django.conf:settings', namespace='CELERY')

#автоматически подцеплять наши tasks
app.autodiscover_tasks()


#@app.task(bind=True)
#def debug_task(self):
#    print('Request: {0!r}'.format(self.request))

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')