"""Модели базы данных — User, Channel, RemoverRequest"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    # когда первый раз зашел в бота
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # сколько раз обрабатывал фото
    download_count: Mapped[int] = mapped_column(default=0)
    # язык интерфейса: ru / uz / en
    language: Mapped[str] = mapped_column(String(5), default="ru")
    # модель rembg по умолчанию для этого юзера
    default_model: Mapped[str] = mapped_column(String(50), default="u2net")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id канала в Telegram (например -1001234567890)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    # название для отображения юзеру
    title: Mapped[str] = mapped_column(String(255))
    # ссылка на канал (для кнопки "Подписаться")
    invite_link: Mapped[str] = mapped_column(String(255))
    # когда добавлен
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


class RemoverRequest(Base):
    """Запись об обработке фото (удаление фона)"""
    __tablename__ = "remover_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # telegram_id пользователя
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    # имя rembg-модели, например "u2net"
    model_used: Mapped[str] = mapped_column(String(50))
    # размер входного файла в КБ
    input_size_kb: Mapped[int] = mapped_column(Integer)
    # размер выходного файла в КБ
    output_size_kb: Mapped[int] = mapped_column(Integer)
    # разрешение исходника, например "1920x1080"
    input_resolution: Mapped[str] = mapped_column(String(20))
    # время обработки в миллисекундах
    processing_time_ms: Mapped[int] = mapped_column(Integer)
    # цвет фона или None (прозрачный) — "white" / "black" / "green" / "#RRGGBB" / "image"
    bg_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # когда обработано
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<RemoverRequest user={self.user_id} model={self.model_used} "
            f"t={self.processing_time_ms}ms>"
        )
