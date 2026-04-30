# Telegram Background Remover Bot

Telegram-бот для удаления фона с фотографий. Обработка происходит **локально через rembg** — фотографии не отправляются на сторонние API.

## Возможности

- Удаление фона с фото / документа (jpeg, png, webp), результат — PNG с прозрачностью.
- Две модели на выбор:
  - **u2net** — универсальная, баланс качества и скорости.
  - **isnet-general-use** — выше качество, чуть медленнее.
- Замена фона на сплошной цвет (белый / чёрный / зелёный / прозрачный) или **свою картинку**.
- Ресайз результата: оригинал / 512px / 1024px / 512×512 квадрат с прозрачным паддингом.
- Защита от decompression-bomb, лимит 20 МБ и 4096px.
- Concurrency-лимит (`asyncio.Semaphore(2)`) — не больше двух параллельных обработок.
- Мультиязычность: русский / узбекский (латиница) / английский.
- Админ-панель: статистика, обязательные подписки на каналы, рассылка.
- Rate-limit: 5 фото/мин на юзера.

## Стек

- Python 3.12, aiogram 3.x
- rembg + onnxruntime (CPU) + Pillow
- PostgreSQL 16 + asyncpg + SQLAlchemy 2.0 (async)
- Docker Compose
- uvloop (ускорение asyncio)

## Быстрый старт

```bash
cp .env.example .env
# заполнить BOT_TOKEN и ADMIN_IDS

docker compose up -d --build
docker compose logs -f bot
```

При первом build Docker скачает в образ две модели rembg (`u2net` + `isnet-general-use`, ~350 МБ суммарно) — первый запрос к боту не ждёт загрузки моделей. Итоговый размер образа ~1.3 ГБ.

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота |
| `/menu` | Главное меню |
| `/profile` | Мой профиль |
| `/help` | Помощь |
| `/language` | Сменить язык интерфейса |
| `/settings` | Выбор модели rembg по умолчанию |
| `/admin` | Админ-панель (только для ADMIN_IDS) |
| `/stats` | Статистика обработок (admin) |

## Структура проекта

```
bot/
├── main.py              — точка входа, retry-loop polling, прогрев rembg в фоне
├── config.py            — pydantic-settings (PostgreSQL, лимиты, модель по умолчанию)
├── i18n.py              — переводы ru/uz/en + detect_language() + t()
├── emojis.py            — премиум-эмодзи для inline-кнопок
├── database/
│   ├── __init__.py      — engine + async_session (asyncpg)
│   ├── models.py        — User, Channel, RemoverRequest
│   └── crud.py          — CRUD-обёртки
├── handlers/
│   ├── start.py         — /start, /menu, /profile, /help, /language, подписка
│   ├── admin.py         — /admin, /stats, рассылка, каналы
│   └── remover.py       — приём фото, удаление фона, постобработка (фон/размер)
├── middlewares/
│   ├── subscription.py  — обязательная подписка на каналы
│   └── rate_limit.py    — 5 фото/мин на юзера
├── keyboards/
│   ├── inline.py        — главное меню, /settings, выбор фона/размера
│   └── admin.py         — админ-панель
├── services/
│   ├── remover.py       — rembg-сервис (LRU=2 сессии, compose_result, decompression-bomb защита)
│   └── cache.py         — кэш cutout-PNG в RAM (TTL 1ч, лимит 200 МБ)
└── utils/
    └── commands.py      — set_default_commands / set_user_commands
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `BOT_TOKEN` | Токен от @BotFather | обязательно |
| `ADMIN_IDS` | ID админов через запятую | — |
| `ADMIN_USERNAME` | Юзернейм админа для подписи | admin |
| `DB_HOST` | Хост PostgreSQL | postgres |
| `DB_PORT` | Порт PostgreSQL | 5432 |
| `DB_NAME` | Имя БД | remover_bot |
| `DB_USER` | Пользователь БД | bot_user |
| `DB_PASSWORD` | Пароль БД | changeme |
| `MAX_INPUT_MB` | Макс. размер входного файла (МБ) | 20 |
| `MAX_RESOLUTION` | Макс. разрешение по большей стороне (px) | 4096 |
| `DEFAULT_MODEL` | Модель rembg по умолчанию | u2net |
| `BOT_API_URL` | URL Local Bot API (для файлов >20 МБ) | https://api.telegram.org |

## Как работает обработка

1. Юзер присылает фото / документ-картинку.
2. Бот валидирует (формат, размер, разрешение, защита от decompression-bomb).
3. Если разрешение > `MAX_RESOLUTION` — ресайз с сохранением пропорций.
4. `rembg.remove()` вырезает объект, результат — RGBA-PNG с альфа-каналом.
5. PNG складывается в RAM-кэш под коротким `request_id` (8 hex-символов).
6. Юзер получает результат как **document** (`send_document`, чтобы Telegram не убил прозрачность).
7. Под результатом — кнопки постобработки: смена фона / размера / возврат в меню.
8. Любая постобработка применяется к оригинальному cutout'у из кэша — комбинировать фон и размер можно как угодно, бесконечно.

## Архитектурные решения

- **На диск ничего не пишется** — весь pipeline в памяти через `BytesIO`. Не накапливается мусор, не нужна очистка `/tmp`.
- **LRU=2 rembg-сессии** — две модели одновременно держим в памяти, остальные эвиктятся. Полная инициализация InferenceSession занимает 10-30 сек, кэш сессии экономит это время.
- **Прогрев модели в фоне** — `_get_session(default_model)` выполняется через `asyncio.create_task`, polling запускается сразу. Первый запрос может подождать 1-2 сек если прогрев ещё идёт.
- **Состояние постобработки в callback_data** — формат `bg_apply:{rid}:{color}:{current_size}` и аналогично для размера. Текущий выбор не теряется при переключениях.
- **Retry-loop в polling** — сетевые сбои (`ServerDisconnectedError`) логируются и polling переподключается через 5 сек, контейнер не падает.
- **Docker-логи лимитированы** — 10 МБ × 3 файла на сервис, не разрастаются.

## Эксплуатация

```bash
# логи
docker compose logs -f bot
docker compose logs -f postgres

# перезапуск
docker compose restart bot

# полная пересборка (после правки Dockerfile)
docker compose down
docker compose up -d --build

# бэкап БД
docker compose exec postgres pg_dump -U bot_user remover_bot > backup.sql
```

## Требования к серверу

- Минимум: 1 CPU, 2 ГБ RAM (две rembg-сессии × ~500 МБ + cutout-кэш до 200 МБ + базовый footprint).
- Рекомендуется: 2 CPU, 4 ГБ RAM при заметной нагрузке.
- Диск: ~2 ГБ под Docker-образ + рост `postgres-data` (~200 байт на запрос).
