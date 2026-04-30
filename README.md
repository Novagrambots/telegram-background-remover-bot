# bot_4_remover

Telegram-бот для удаления фона с фотографий. Обработка происходит локально через библиотеку rembg — данные не отправляются на сторонние серверы.

## Стек

- Python 3.11, aiogram 3.x
- rembg (u2net, isnet-general-use, silueta) + onnxruntime CPU
- Pillow для работы с изображениями
- SQLite + aiosqlite (без PostgreSQL)
- Docker Compose

## Быстрый старт

```bash
cd bot_4_remover
cp .env.example .env
# Заполнить BOT_TOKEN и ADMIN_IDS в .env

docker compose up -d --build
```

При первом build Docker скачает модель u2net (~170 МБ) и закэширует в volume.

## Команды бота

| Команда | Описание |
|---------|----------|
| /start | Запустить бота |
| /menu | Главное меню |
| /profile | Мой профиль |
| /help | Помощь |
| /language | Сменить язык |
| /settings | Настройки (модель, цвет фона) |
| /admin | Админ-панель |
| /stats | Статистика (только для админов) |

## Структура проекта

```
bot/
├── main.py, config.py, i18n.py, emojis.py
├── database/        — User, Channel, RemoverRequest (TODO)
├── handlers/        — start, admin, __todo_domain (TODO)
├── middlewares/     — subscription, rate_limit
├── keyboards/       — inline, admin
├── services/        — __todo_domain (TODO: rembg сервис)
└── utils/           — commands
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| BOT_TOKEN | Токен от @BotFather | обязательно |
| ADMIN_IDS | ID админов через запятую | — |
| DB_URL | URL базы данных | sqlite+aiosqlite:///data/bot.db |
| MAX_INPUT_MB | Макс. размер входного файла (МБ) | 20 |
| MAX_RESOLUTION | Макс. разрешение (px) | 4096 |
| DEFAULT_MODEL | Модель rembg | u2net |
