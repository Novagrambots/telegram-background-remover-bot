"""CRUD операции с базой данных"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Channel, RemoverRequest, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    language: str | None = None,
) -> User:
    """Получить юзера или создать нового"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language=language or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    """Получить язык юзера (по умолчанию ru)"""
    result = await session.execute(
        select(User.language).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    """Обновить язык юзера"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language = language
        await session.commit()


async def update_user_model(
    session: AsyncSession, telegram_id: int, model: str
) -> None:
    """Обновить модель rembg для юзера"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.default_model = model
        await session.commit()


async def increment_user_download_count(
    session: AsyncSession, telegram_id: int
) -> None:
    """Увеличить счётчик обработок юзера на 1"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.download_count += 1
        await session.commit()


async def get_active_channels(session: AsyncSession) -> list[Channel]:
    """Получить все каналы для обязательной подписки"""
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


# === Админские функции ===

async def add_channel(
    session: AsyncSession,
    channel_id: int,
    title: str,
    invite_link: str,
) -> Channel:
    """Добавить канал для обязательной подписки"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")

    channel = Channel(
        channel_id=channel_id,
        title=title,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    """Удалить канал. Возвращает True если удалён"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False

    await session.delete(channel)
    await session.commit()
    return True


async def get_user_stats(session: AsyncSession) -> dict:
    """Статистика: всего юзеров, за сегодня, обработок"""
    from sqlalchemy import func as sa_func

    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    downloads = await session.execute(
        select(sa_func.sum(User.download_count))
    )
    total_downloads = downloads.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_downloads": total_downloads,
        "total_channels": total_channels,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    """Получить все telegram_id юзеров для рассылки"""
    result = await session.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]


async def save_remover_request(
    session: AsyncSession,
    user_id: int,
    model_used: str,
    input_size_kb: int,
    output_size_kb: int,
    input_resolution: str,
    processing_time_ms: int,
    bg_color: str | None = None,
) -> RemoverRequest:
    """Сохранить запись об обработке фото"""
    req = RemoverRequest(
        user_id=user_id,
        model_used=model_used,
        input_size_kb=input_size_kb,
        output_size_kb=output_size_kb,
        input_resolution=input_resolution,
        processing_time_ms=processing_time_ms,
        bg_color=bg_color,
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)
    return req


async def get_user_remover_stats(
    session: AsyncSession, telegram_id: int
) -> dict:
    """Статистика обработок конкретного юзера: всего, среднее время, любимая модель"""
    from sqlalchemy import func as sa_func

    total = await session.execute(
        select(sa_func.count(RemoverRequest.id))
        .where(RemoverRequest.user_id == telegram_id)
    )
    total_count = total.scalar() or 0

    avg = await session.execute(
        select(sa_func.avg(RemoverRequest.processing_time_ms))
        .where(RemoverRequest.user_id == telegram_id)
    )
    avg_ms = int(avg.scalar() or 0)

    fav = await session.execute(
        select(RemoverRequest.model_used, sa_func.count(RemoverRequest.id))
        .where(RemoverRequest.user_id == telegram_id)
        .group_by(RemoverRequest.model_used)
        .order_by(sa_func.count(RemoverRequest.id).desc())
        .limit(1)
    )
    fav_row = fav.first()
    favorite_model = fav_row[0] if fav_row else None

    return {
        "total": total_count,
        "avg_ms": avg_ms,
        "favorite_model": favorite_model,
    }


async def get_user_default_model(
    session: AsyncSession, telegram_id: int
) -> str:
    """Возвращает выбранную юзером модель rembg (или дефолтную)"""
    from bot.config import settings as _settings
    result = await session.execute(
        select(User.default_model).where(User.telegram_id == telegram_id)
    )
    model = result.scalar_one_or_none()
    return model or _settings.default_model
