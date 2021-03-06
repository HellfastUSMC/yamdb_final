# YaMDb project
### Link
http://84.252.142.37
or
http://pisswasser.servebeer.com
### Test link to api
- Выводит список обзоров по произведению с id 1
```
http://84.252.142.37/api/v1/titles/1/reviews/
```
### Workflow Status
![yamdb_final workflow](https://github.com/HellfastUSMC/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
### Описание
Проект YaMDb собирает отзывы пользователей на различные произведения.
### Технологии
Python 3.7
Django 2.2.16
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/Scripts/activate
``` 
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Запустите сервер
```
python manage.py runserver
```
### Запуск проекта в docker-compose
- Перейдите в папку /infra и выполните команду для создания контейнеров
```
sudo docker compose up
```
- Для выполнения миграций, создания супер-пользователя, загрузки тестовых данных в БД и сбора статики введите команды
```
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py load_data
sudo docker-compose exec web python manage.py collectstatic
```


### Загрузка данных из csv файлов
- В папке api_yamdb/api_yamdb выполните команду для наполнения тестовыми данными:
```
python manage.py load_data
```
### Описание .env файла
- Структура .env файла:
```
# Укажите, что используете postgresql
DB_ENGINE=django.db.backends.postgresql
# Укажите имя созданной базы данных
DB_NAME=DB_NAME
# Укажите имя пользователя
POSTGRES_USER=USERNAME
# Укажите пароль для пользователя
POSTGRES_PASSWORD=PASSWORD
# Укажите localhost
DB_HOST=127.0.0.1
# Укажите порт для подключения к базе
DB_PORT=5432
```

### Описание API
- API проекта находится по адресу http://127.0.0.1:8000/redoc/#section/Opisanie
### Пример запроса к API 
- CATEGORIES Получение списка всех категорий
```
GET CATEGORIES http://127.0.0.1:8000/api/v1/categories/
RESPONSE 200 (Удачное выполнение запроса)
[
  {
  "count": 0,
  "next": "string",
  "previous": "string",
   "results": [
                {
                 "name": "string",
                "slug": "string"
                }
                ...
              ]
  }
]
```
### Автор
- Александр Набиев, когорта 26, факультет backend-разработки Yandex Practicum.
