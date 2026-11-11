# Flask application — лабораторна робота №6

Додаток містить модуль публікацій із CRUD-операціями на Flask, Flask-SQLAlchemy, SQLAlchemy 2.x, Flask-Migrate, Flask-WTF, Jinja2 та Bootstrap 5. Попередні модулі резюме, контактів, користувачів і товарів збережені.

## Запуск на Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m flask --app run.py db upgrade
python -m flask --app run.py run
```

Після запуску відкрийте `http://127.0.0.1:8080/`. Розділ публікацій доступний за адресою `http://127.0.0.1:8080/post`.

## Міграції бази даних

```powershell
python -m flask --app run.py db history
python -m flask --app run.py db migrate -m "Опис змін"
python -m flask --app run.py db upgrade
```

SQLite-файл створюється у `instance/data.sqlite`. За замовчуванням використовується змінна `DATABASE_URL=sqlite:///data.sqlite` з `.env`.

## Модульні тести

```powershell
python -m unittest discover -s tests -v
```

Тести CRUD для публікацій розміщені у `tests/test_posts.py`. Для тестування використовується окрема база SQLite в пам'яті.

## Маршрути публікацій

| Метод | Шлях | Дія |
|---|---|---|
| GET, POST | `/post/create` | Створення поста |
| GET | `/post` | Список активних постів, новіші зверху |
| GET | `/post/<id>` | Деталі поста |
| GET, POST | `/post/<id>/update` | Редагування поста |
| GET, POST | `/post/<id>/delete` | Підтвердження та видалення поста |

Автором нового поста стає користувач із Flask session. Якщо користувач не авторизований, використовується `Anonymous`.
