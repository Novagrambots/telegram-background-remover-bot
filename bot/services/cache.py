"""In-memory LRU-кэш cutout-результатов для постобработки (замена фона/размер).

Хранит готовый PNG (RGBA, прозрачный фон) по короткому request_id, который
кладётся в callback_data inline-кнопок. TTL — 1 час, лимит — 200 МБ
суммарно по байтам (защита от OOM при большом количестве крупных PNG).
Без зависимостей; чистится фоновой задачей в main.py._background_cleanup().
"""
from __future__ import annotations

import logging
import secrets
import time
from collections import OrderedDict

logger = logging.getLogger(__name__)

# request_id (8 hex chars) -> (cutout_png_bytes, ts, model_used)
_cache: OrderedDict[str, tuple[bytes, float, str]] = OrderedDict()

# конфиг
TTL_SECONDS = 60 * 60  # 1 час
MAX_TOTAL_BYTES = 200 * 1024 * 1024  # 200 МБ суммарно

# текущий суммарный вес (поддерживается инкрементально для O(1))
_total_bytes = 0


def _evict_until_fit() -> None:
    """Эвиктит самые старые записи, пока суммарный вес > MAX_TOTAL_BYTES"""
    global _total_bytes
    while _total_bytes > MAX_TOTAL_BYTES and _cache:
        rid, (data, _, _) = _cache.popitem(last=False)
        _total_bytes -= len(data)
        logger.debug("Cutout-кэш: эвикт %s (%d KB) по лимиту байт", rid, len(data) // 1024)


def put(cutout_png: bytes, model_used: str, request_id: str | None = None) -> str:
    """Кладёт результат в кэш и возвращает request_id.

    Если передан request_id — использует его (перезаписывая старое значение,
    чтобы не плодить новые ключи для постобработок одной и той же картинки).
    Иначе генерирует новый.
    """
    global _total_bytes

    if request_id is None:
        request_id = secrets.token_hex(4)  # 8 символов

    # снять прежний вес если такой rid уже был
    old = _cache.pop(request_id, None)
    if old is not None:
        _total_bytes -= len(old[0])

    _cache[request_id] = (cutout_png, time.time(), model_used)
    _total_bytes += len(cutout_png)
    _cache.move_to_end(request_id)

    _evict_until_fit()
    return request_id


def get(request_id: str) -> tuple[bytes, str] | None:
    """Возвращает (cutout_png, model_used) или None если просрочено/не найдено"""
    global _total_bytes
    item = _cache.get(request_id)
    if item is None:
        return None
    cutout, ts, model = item
    if time.time() - ts > TTL_SECONDS:
        _cache.pop(request_id, None)
        _total_bytes -= len(cutout)
        return None
    _cache.move_to_end(request_id)
    return cutout, model


def cleanup_expired() -> int:
    """Удаляет протухшие записи. Вызывается из фоновой очистки. Возвращает кол-во удалённых."""
    global _total_bytes
    now = time.time()
    expired = [
        rid for rid, (_, ts, _) in _cache.items()
        if now - ts > TTL_SECONDS
    ]
    for rid in expired:
        item = _cache.pop(rid, None)
        if item is not None:
            _total_bytes -= len(item[0])
    if expired:
        logger.debug("Cutout-кэш: удалено %d просроченных", len(expired))
    return len(expired)
