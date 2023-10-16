"""
ASGI config for President_fish project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoprENVIRONMENT=development
SECRET_KEY=6--sgw^@$y!b1wjw-o$wx&9h#8&a(w!r6hytw0w=_4p4)55@vv
DEBUG=1
ALLOWED_HOSTS=localhost 127.0.0.1 35.228.232.64
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=django_db
POSTGRES_USER=django_user
POSTGRES_PASSWORD=12345666
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

SMS_RU_API_ID=D4B0D541-528C-B55C-BEA4-53302139E0FD

CELERY_BROKER_URL=localhost:6379
CELERY_RESULT_BACKEND=localhost:6379
CELERY_ACCEPT_CONTENT=application/json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=jsonoject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'president_fish.settings')

application = get_asgi_application()
