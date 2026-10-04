# НЕМК Соціальна Мережа

Навчальний проект для [Ніжинського електромеханічного коледжу](https://nemk.com.ua/).

## Стек технологій

| Категорія | Технологія |
|---|---|
| Backend | Python 3.11+, Django 5.0 |
| Real-time | Django Channels 4, WebSocket |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| БД (розробка) | SQLite |
| БД (продакшн) | PostgreSQL |
| ASGI-сервер | Daphne |

---

## Функціонал

- Реєстрація / вхід / вихід (2 ролі: користувач, адміністратор)
- Профіль користувача (аватар, обкладинка, біографія)
- Стрічка новин (публікації, лайки, коментарі, репости)
- Друзі (запити, прийняття, відхилення, підписки)
- Групи та спільноти (створення, вступ, модерація)
- Чат у реальному часі (WebSocket + HTTP fallback)
- Сповіщення (real-time бейдж, налаштування)
- Адмін-панель Django з повним контролем над даними

---

## Швидкий старт

### 1. Клонуйте репозиторій

```bash
git clone https://github.com/your-repo/nemk_social.git
cd nemk_social
```

### 2. Створіть та активуйте віртуальне середовище

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Встановіть залежності

```bash
pip install -r requirements.txt
```

### 4. Налаштуйте змінні середовища

```bash
copy .env.example .env   # Windows
# або
cp .env.example .env     # Linux/macOS
```

Відредагуйте `.env` — замініть `DJANGO_SECRET_KEY`.

### 5. Застосуйте міграції

```bash
python manage.py migrate
```

### 6. Створіть суперкористувача (адміністратора)

```bash
python manage.py createsuperuser
```

Після створення увійдіть в адмін-панель `/admin/` і встановіть полю `role = admin`.

### 7. Зберіть статичні файли (для продакшну)

```bash
python manage.py collectstatic
```

### 8. Запустіть сервер

```bash
# Розробка (Daphne — підтримує WebSocket)
daphne -p 8000 nemk_social.asgi:application

# Або стандартний Django (без WebSocket, тільки HTTP polling)
python manage.py runserver
```

Відкрийте в браузері: **http://127.0.0.1:8000**

---

## Структура проекту

```
nemk_social/
├── accounts/          # Користувачі, реєстрація, профілі
├── posts/             # Публікації, лайки, коментарі
├── friends/           # Друзі, підписки
├── groups/            # Групи та спільноти
├── chat/              # Чат (WebSocket + HTTP)
├── notifications/     # Сповіщення
├── templates/         # HTML-шаблони
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   ├── posts/
│   ├── friends/
│   ├── groups/
│   ├── chat/
│   └── notifications/
├── static/
│   ├── css/main.css
│   └── js/main.js
├── media/             # Завантажені файли користувачів
├── nemk_social/       # Налаштування Django
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── .env.example
```

---

## URL-маршрути

| URL | Опис | Доступ |
|---|---|---|
| `/` | Головна / стрічка | Всі |
| `/register/` | Реєстрація | Гості |
| `/login/` | Вхід | Гості |
| `/profile/<username>/` | Профіль | Авторизовані |
| `/profile/edit/` | Редагування профілю | Свій |
| `/feed/` | Стрічка новин | Авторизовані |
| `/friends/` | Друзі та запити | Авторизовані |
| `/groups/` | Список груп | Авторизовані |
| `/groups/<id>/` | Сторінка групи | Авторизовані |
| `/chat/` | Повідомлення | Авторизовані |
| `/chat/<id>/` | Розмова | Учасник |
| `/notifications/` | Сповіщення | Авторизовані |
| `/search/` | Пошук користувачів | Авторизовані |
| `/admin/` | Адмін-панель | Адміністратори |

---

## Продакшн (коротко)

1. Встановити `DJANGO_DEBUG=False` в `.env`
2. Налаштувати PostgreSQL
3. Встановити Redis і оновити `CHANNEL_LAYERS` в `settings.py`
4. Запустити через Daphne + Nginx з SSL-сертифікатом

---

*© 2024 НЕМК — [nemk.com.ua](https://nemk.com.ua/)*
