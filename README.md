🚀 Запуск проекта
Для запуска проекта выполните следующие действия:

Перейдите в директорию infra/:


```cd infra```

Запустите контейнеры:


```docker compose up```

Проект автоматически поднимет:

PostgreSQL

Django backend + Gunicorn

React frontend

Nginx


Суперпользователь можно создать вручную:

```docker exec -it infra-backend-1 python manage.py createsuperuser```

