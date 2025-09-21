Учебный проект в рамках яндекс практикума, представляющий собой реализацию backend - части веб приложения на Django, являющего собой подобие инстаграмма.

Запуск проекта

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

Проект будет доступен по адресу localhost.
Админка достпуна по адресу: localhost/admin


Суперпользователь можно создать вручную:

```docker exec -it foodgram-backend python manage.py createsuperuser```

Так как volumes не перенести, можно воспользоваться postman_collection для создания тестовых данных

Ссылка на докерхаб: https://hub.docker.com/repositories/altok1ef

Ссылка на гитхаб: https://github.com/AltoKlef/foodgram-st

Почему прошлую работу назвали плагиатом? Я не списывал, можно коммиты посмотреть.
