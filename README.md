# YaMDb
## Описание проекта
Проект YaMDb собирает отзывы пользователей на различные произведения.
Документация проекта доступна на сервере: https://avnikitenko.ddns.net/redoc/ (если домен недоступен, подключайтесь по IP: http://84.201.155.158/redoc/)


## Информация о проекте
API для проекта YaMDb (ДЗ курса Яндекс.Практикум)  
**Автор:** Никитенко Алексей, когорта 27

![yamdb_workflow.yml](https://github.com/avnikitenko/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Локальный запуск проекта

Клонировать репозиторий и перейти в папку infra в командной строке:

```
git clone https://github.com/avnikitenko/yamdb_final.git
```

```
cd yamdb_final/infra
```

Выполнить сборку docker compose

```
docker-compose up -d --build
```

Выполнить миграции

```
docker-compose exec web python manage.py migrate
```

Выполнить сборку статики

```
docker-compose exec web python manage.py collectstatic --no-input
```

Открыть браузер, перейти на localhost/redoc... PROFIT!