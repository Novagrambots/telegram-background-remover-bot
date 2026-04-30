"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['camera']} Я помогу тебе удалить фон с фотографии — "
            "быстро, локально и бесплатно!\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            f"Просто отправь мне фотографию — и я уберу фон! {E['plane']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['camera']} Rasmdan fonni olib tashlashga yordam beraman — "
            "tez, mahalliy va bepul!\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            f"Menga rasm yuboring — men fonni olib tashlayman! {E['plane']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['camera']} I'll help you remove the background from a photo — "
            "fast, local and free!\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            f"Just send me a photo — and I'll remove the background! {E['plane']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.process": {
        "ru": "Удалить фон",
        "uz": "Fonni olib tashlash",
        "en": "Remove background",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "btn.settings": {
        "ru": "Настройки",
        "uz": "Sozlamalar",
        "en": "Settings",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Обработок (всего): {{downloads}}\n"
            f"{E['gear']} Модель: <code>{{model}}</code>\n"
        ),
        "uz": (
            f"{E['profile']} <b>Mening profilim</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Ishlovlar (jami): {{downloads}}\n"
            f"{E['gear']} Model: <code>{{model}}</code>\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Processed (total): {{downloads}}\n"
            f"{E['gear']} Model: <code>{{model}}</code>\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь фото — получишь изображение без фона (PNG)\n"
            f"{E['star']} Обработка происходит локально, данные не отправляются на сторонние серверы\n"
            f"{E['star']} Максимальный размер файла: {{max_mb}} МБ\n"
            f"{E['star']} Максимальное разрешение: {{max_res}}x{{max_res}} px\n"
            f"{E['lock']} Анимации и видео не поддерживаются\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Rasm yuboring — fonsiz tasvir olasiz (PNG)\n"
            f"{E['star']} Ishlov mahalliy bo'ladi, ma'lumotlar uchinchi tomonlarga yuborilmaydi\n"
            f"{E['star']} Maksimal fayl hajmi: {{max_mb}} MB\n"
            f"{E['star']} Maksimal o'lcham: {{max_res}}x{{max_res}} px\n"
            f"{E['lock']} Animatsiyalar va videolar qo'llab-quvvatlanmaydi\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a photo — get an image without background (PNG)\n"
            f"{E['star']} Processing is local, data is not sent to third-party servers\n"
            f"{E['star']} Maximum file size: {{max_mb}} MB\n"
            f"{E['star']} Maximum resolution: {{max_res}}x{{max_res}} px\n"
            f"{E['lock']} Animations and videos are not supported\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['camera']} Этот бот удаляет фон с фотографий — "
            "быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['camera']} Bu bot rasmlardan fonni olib tashlaydi — "
            "tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'l:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bos"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['camera']} This bot removes backgrounds from photos — "
            "fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Sen hali barcha kanallarga obuna bo'lmading:</b>\n\n"
            f"Obuna bo'l va «{E['check']} Obunani tekshirish» tugmasini qayta bos."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь фотографию для удаления фона."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            "Fonni olib tashlash uchun rasm yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send a photo to remove its background."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой</b>\n\nМаксимальный размер: {{max_mb}} МБ.",
        "uz": f"{E['package']} <b>Fayl juda katta</b>\n\nMaksimal hajm: {{max_mb}} MB.",
        "en": f"{E['package']} <b>File too large</b>\n\nMaximum size: {{max_mb}} MB.",
    },
    "error.resolution_too_large": {
        "ru": f"{E['warning']} <b>Слишком большое разрешение</b>\n\nМаксимум: {{max_res}}x{{max_res}} пикселей.",
        "uz": f"{E['warning']} <b>O'lcham juda katta</b>\n\nMaksimum: {{max_res}}x{{max_res}} piksel.",
        "en": f"{E['warning']} <b>Resolution too large</b>\n\nMaximum: {{max_res}}x{{max_res}} pixels.",
    },
    "error.not_image": {
        "ru": f"{E['cross']} <b>Это не фотография</b>\n\nОтправь обычное фото или изображение как файл.",
        "uz": f"{E['cross']} <b>Bu rasm emas</b>\n\nOddiy rasm yoki fayl sifatida rasm yuboring.",
        "en": f"{E['cross']} <b>This is not a photo</b>\n\nSend a regular photo or image as a file.",
    },
    "error.processing_failed": {
        "ru": f"{E['cross']} <b>Ошибка обработки</b>\n\nНе удалось обработать изображение. Попробуй другое фото.",
        "uz": f"{E['cross']} <b>Ishlov xatosi</b>\n\nRasmni qayta ishlashda xatolik. Boshqa rasm sinab ko'ring.",
        "en": f"{E['cross']} <b>Processing error</b>\n\nFailed to process the image. Try a different photo.",
    },
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nПопробуй ещё раз через пару минут.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nBir necha daqiqadan keyin qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nPlease try again in a few minutes.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Что-то пошло не так</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Nimadir xato ketdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>Something went wrong</b>\n\nPlease try again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },

    # === Удаление фона (доменные ключи) ===
    "remover.prompt": {
        "ru": (
            f"{E['camera']} <b>Отправь фотографию</b>\n\n"
            "Пришли мне фото или изображение как файл — я удалю фон и верну "
            "PNG с прозрачным фоном.\n\n"
            f"{E['info']} Лимит: {{max_mb}} МБ, до {{max_res}}x{{max_res}} px."
        ),
        "uz": (
            f"{E['camera']} <b>Rasm yuboring</b>\n\n"
            "Menga rasm yoki fayl ko'rinishidagi tasvirni yuboring — men fonni "
            "olib tashlayman va shaffof PNG qaytaraman.\n\n"
            f"{E['info']} Limit: {{max_mb}} MB, {{max_res}}x{{max_res}} px gacha."
        ),
        "en": (
            f"{E['camera']} <b>Send a photo</b>\n\n"
            "Send me a photo or image-as-file — I'll remove the background and "
            "return a PNG with transparency.\n\n"
            f"{E['info']} Limit: {{max_mb}} MB, up to {{max_res}}x{{max_res}} px."
        ),
    },
    "remover.processing": {
        "ru": f"{E['clock']} <b>Обрабатываю...</b>\n\nЭто займёт несколько секунд.",
        "uz": f"{E['clock']} <b>Ishlamoqdaman...</b>\n\nBir necha soniya kutib turing.",
        "en": f"{E['clock']} <b>Processing...</b>\n\nThis will take a few seconds.",
    },
    "remover.done": {
        "ru": (
            f"{E['check']} <b>Готово!</b>\n\n"
            f"{E['gear']} Модель: <code>{{model}}</code>\n"
            f"{E['package']} Разрешение: <code>{{resolution}}</code>\n"
            f"{E['lightning']} Время: <b>{{ms}} мс</b>"
        ),
        "uz": (
            f"{E['check']} <b>Tayyor!</b>\n\n"
            f"{E['gear']} Model: <code>{{model}}</code>\n"
            f"{E['package']} O'lcham: <code>{{resolution}}</code>\n"
            f"{E['lightning']} Vaqt: <b>{{ms}} ms</b>"
        ),
        "en": (
            f"{E['check']} <b>Done!</b>\n\n"
            f"{E['gear']} Model: <code>{{model}}</code>\n"
            f"{E['package']} Resolution: <code>{{resolution}}</code>\n"
            f"{E['lightning']} Time: <b>{{ms}} ms</b>"
        ),
    },
    "remover.result_simple": {
        "ru": (
            f"{E['check']} <b>Готово!</b>\n\n"
            f"{E['gear']} Модель: <code>{{model}}</code>"
        ),
        "uz": (
            f"{E['check']} <b>Tayyor!</b>\n\n"
            f"{E['gear']} Model: <code>{{model}}</code>"
        ),
        "en": (
            f"{E['check']} <b>Done!</b>\n\n"
            f"{E['gear']} Model: <code>{{model}}</code>"
        ),
    },
    "remover.settings": {
        "ru": (
            f"{E['gear']} <b>Настройки</b>\n\n"
            f"Текущая модель: <code>{{model}}</code>\n\n"
            f"{E['bulb']} <b>Какую выбрать?</b>\n"
            f"• <b>u2net</b> — баланс качества и скорости\n"
            f"• <b>isnet-general-use</b> — выше качество, чуть медленнее"
        ),
        "uz": (
            f"{E['gear']} <b>Sozlamalar</b>\n\n"
            f"Joriy model: <code>{{model}}</code>\n\n"
            f"{E['bulb']} <b>Qaysi birini tanlash?</b>\n"
            f"• <b>u2net</b> — sifat va tezlik balansi\n"
            f"• <b>isnet-general-use</b> — yuqori sifat, biroz sekinroq"
        ),
        "en": (
            f"{E['gear']} <b>Settings</b>\n\n"
            f"Current model: <code>{{model}}</code>\n\n"
            f"{E['bulb']} <b>Which one?</b>\n"
            f"• <b>u2net</b> — balanced quality / speed\n"
            f"• <b>isnet-general-use</b> — higher quality, slightly slower"
        ),
    },
    "remover.model_set": {
        "ru": f"{E['check']} Модель изменена на <code>{{model}}</code>",
        "uz": f"{E['check']} Model <code>{{model}}</code> ga o'zgartirildi",
        "en": f"{E['check']} Model switched to <code>{{model}}</code>",
    },
    "remover.bg_menu": {
        "ru": f"{E['edit']} <b>Выбери фон:</b>",
        "uz": f"{E['edit']} <b>Fonni tanlang:</b>",
        "en": f"{E['edit']} <b>Choose a background:</b>",
    },
    "remover.size_menu": {
        "ru": f"{E['package']} <b>Выбери размер:</b>",
        "uz": f"{E['package']} <b>O'lchamni tanlang:</b>",
        "en": f"{E['package']} <b>Choose a size:</b>",
    },
    "remover.send_prompt": {
        "ru": f"{E['camera']} Пришли фото в чат — обработаю и пришлю результат без фона.",
        "uz": f"{E['camera']} Chatga rasm yuboring — fonsiz natijani qaytaraman.",
        "en": f"{E['camera']} Send a photo to the chat — I will return it without background.",
    },
    "remover.bg_image_prompt": {
        "ru": f"{E['camera']} Отправь фото-фон, на который наложить вырезанный объект.",
        "uz": f"{E['camera']} Kesilgan ob'ektni ustiga qo'yish uchun fon rasm yuboring.",
        "en": f"{E['camera']} Send a background photo to place the cutout onto.",
    },
    "remover.expired": {
        "ru": f"{E['clock']} Результат больше недоступен — отправь фото заново.",
        "uz": f"{E['clock']} Natija muddati o'tdi — rasmni qaytadan yuboring.",
        "en": f"{E['clock']} Result has expired — please send the photo again.",
    },
    "remover.caption_variant": {
        "ru": f"{E['check']} Готово ({{variant}})",
        "uz": f"{E['check']} Tayyor ({{variant}})",
        "en": f"{E['check']} Done ({{variant}})",
    },

    # Кнопки выбора модели
    "btn.model_u2net": {"ru": "u2net (универсальная)", "uz": "u2net (universal)", "en": "u2net (general)"},
    "btn.model_isnet": {"ru": "isnet-general-use (точная)", "uz": "isnet-general-use (aniq)", "en": "isnet-general-use (precise)"},

    # Кнопки выбора фона / размера
    "btn.bg_change": {"ru": "Заменить фон", "uz": "Fonni almashtirish", "en": "Change background"},
    "btn.size_change": {"ru": "Размер", "uz": "O'lcham", "en": "Size"},
    "btn.bg_transparent": {"ru": "Прозрачный", "uz": "Shaffof", "en": "Transparent"},
    "btn.bg_white": {"ru": "Белый", "uz": "Oq", "en": "White"},
    "btn.bg_black": {"ru": "Чёрный", "uz": "Qora", "en": "Black"},
    "btn.bg_green": {"ru": "Зелёный (chroma)", "uz": "Yashil (chroma)", "en": "Green (chroma)"},
    "btn.bg_image": {"ru": "Своя картинка", "uz": "O'z rasmim", "en": "Custom image"},
    "btn.size_original": {"ru": "Оригинал", "uz": "Original", "en": "Original"},
    "btn.size_512": {"ru": "512 px", "uz": "512 px", "en": "512 px"},
    "btn.size_1024": {"ru": "1024 px", "uz": "1024 px", "en": "1024 px"},
    "btn.size_square": {"ru": "512×512 квадрат", "uz": "512×512 kvadrat", "en": "512×512 square"},
    "btn.home": {"ru": "В главное меню", "uz": "Bosh menyuga", "en": "Main menu"},

    # Админская команда /stats — расширенная
    "admin.remover_stats": {
        "ru": (
            f"{E['chart']} <b>Статистика обработок</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых сегодня: <b>{{today_users}}</b>\n"
            f"{E['download']} Всего обработок: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Ishlovlar statistikasi</b>\n\n"
            f"{E['users']} Jami: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugun yangi: <b>{{today_users}}</b>\n"
            f"{E['download']} Jami ishlovlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Processing stats</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New today: <b>{{today_users}}</b>\n"
            f"{E['download']} Total processed: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Admin panelga kirish huquqing yo'q.",
        "en": f"{E['lock']} You don't have access to the admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['download']} Всего обработок: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['download']} Jami ishlovlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['download']} Total processed: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysanmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar tarqatish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysanmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Bosh menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "cmd.settings": {
        "ru": "Настройки",
        "uz": "Sozlamalar",
        "en": "Settings",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
