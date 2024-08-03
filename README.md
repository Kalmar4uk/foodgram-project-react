# Foodgram
## Foodgram дает возможность размещать рецепты, а так же просматривать рецепты других пользователей, подписываться на авторов, добавлять рецепты в избранное и скачивать файл с ингедиентами для списка покупок

### Рабочий проект доступен по адресу https://foodgram-projects.hopto.org/
### По адресу https://foodgram-projects.hopto.org/api/docs/ доступна документация api redoc

**В проекте используется**
* Django 3.2.16
* Django Rest Framework 3.12.4

### Как запустить проект

*Клонировать репозиторий*
```
git@github.com:Kalmar4uk/foodgram-project-react.git
```

*Находясь в главной директории проекта создать и активировать виртуальное окружение*
```
python -m venv venv
```

*Обновить pip*
```
python -m pip install --upgrade pip
```

*Установить зависимости*
```
pip install -r requirements.txt
```

* При локальном запуске через ```python manage.py runserver``` необходимо выполнить миграции и прогрузить из файла .csv ингредиенты.
* Так же в проекте есть Dockerfiles каждого модуля (бекенд, фронтенд, нгинкс), необходимо перейти в директорию infra ```cd infra```, открыть Docker Desktop и прописать команду ```docker compose up```, после чего выполнить миграции и прогрузить файл .csv внутри контейнера.


*Перейти в директорию с файлом manage.py, создать и выполнить миграции*
```
python manage.py makemigrations
python manage.py migrate
```

### Добавление ингредиентов из файла .csv

*Перейти в директорию с файлом manage.py и прописать команду*
```
python manage.py import_csv file_name.csv --model_name model
```
Где:
* *file_name.csv* - название файла для загрузки
* *--model_name model* - "--model_name" устанавливается для указания модели, "model" - название модели

**После запуска проекта станут доступны эндпоинты**

**Ниже представлен короткий список эндпоинтов для получения рецептов, тегов, ингредиентов**

1. *Получить список всех рецептов:*
```
localhost:8000/api/recipes/
```
   * *Пример ответа:*
   ```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
   ```
2. *Получить список тегов:*
```
localhost:8000/api/tags/
```
   * *Пример ответа:*
   ```
[
  {
    "id": 0,
    "name": "Завтрак",
    "color": "#E26C2D",
    "slug": "breakfast"
  }
]
   ```
3. *Получить список рецептов:*
```
localhost:8000/api/ingredients/
```
   * *Пример ответа:*
   ```
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
   ```
  
**Работу выполнил**
Беспалов Роман https://github.com/Kalmar4uk
