# Video-service
Микросервис предоставляет api взаимодействия с базой данных загруженных видео. Является частью [видеохостинга](https://github.com/orgs/VideoHosting-Platform/repositories)

Сервис отслеживает очередь RabbitMQ. Когда в неё приходит сообщение о загруженном видео, сервис делает запись в БД. Другие сервисы могут напрямую обращаться, чтобы получить, удалить или изменить записи в БД.

## Функции

- CRUD-операции с записями о загруженных видео в Postgres
- Чтение сообщений с RabbitMQ и создание записи в БД 

## Установка и запуск

### Локально

1. Создать БД и пользователя для нее. Указать конфигурацию в .env

2. Запустить RabbitMQ. Связать обменник с очередью. Указать хост брокера и название очереди в .env

2. Применить миграции alembic:

```bash
alembic upgrade head
```

3. Перейти в директорию проекта:

```bash
cd video-service
```

4. Создать виртуальное окружение, перейти в него и установить зависимости:

```bash
pip install -r requirements.txt
```

5. Запустить приложение:

```bash
uvicorn app.main:app
```

### В кластере Kubernetes

Подключиться к кластеру и запустить run.sh:

```bash
. run.sh
```

## Примеры

Пример сообщения, которое приходит из RabbitMQ:

```json
{
"video_id":  "i1fedf2f3fw4f", 
"video_title": "Синий трактор", 
"video_master_playlist_url": "http://localhost:9000/videos/1"
}
```

В БД будет загружено:

```json
{
"title": "Синий трактор", 
"video_url": "http://localhost:9000/videos/1",
"video_id":  "i1fedf2f3fw4f",
"views": 0,
"likes": 0,
"dislikes": 0,
}
```

Получение информации о видео по video_id:

```http
GET http://localhost:8000/video/i1fedf2f3fw4f
```

Пример ответа:

```json
{
"title": "Синий трактор", 
"video_url": "http://localhost:9000/videos/1",
"video_id":  "i1fedf2f3fw4f",
"views": 0,
"likes": 0,
"dislikes": 0,
}
```

Изменение информации о видео:

```http
PUT http://localhost:8000/video/i1fedf2f3fw4f
```

Тело запроса:

```json
{
 "title": "Красный трактор",
 "video_url": "http://localhost:9000/videos/1",
 "video_id": "i1fedf2f3fw4f",
}
```

<b> ВАЖНО! <b> PUT-запросы могут обновить video_url в БД, но не обновляют его в минио

Удаление записи о видео:

```http
DELETE http://localhost:8000/video/i1fedf2f3fw4f
```

Тело запроса:

```json
{
 "video_id": "i1fedf2f3fw4f",
}
```

<b> ВАЖНО! <b> DELETE-запросы могут удалить видео в БД, но не удалят его в минио
