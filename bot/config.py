"""Конфигурация бота — все настройки из .env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str

    # юзернейм бота (для подписи)
    bot_username: str = ""

    # PostgreSQL
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "bot_4_remover"
    db_user: str = "bot_user"
    db_password: str = ""

    # админы бота (через запятую в .env)
    admin_ids: str = ""
    admin_username: str = "admin"

    # URL Local Bot API (опционально — для файлов >50 МБ)
    bot_api_url: str = "https://api.telegram.org"

    # ограничения для обработки фото
    max_input_mb: int = 20
    max_resolution: int = 4096

    # модель rembg по умолчанию
    default_model: str = "u2net"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def admin_id_list(self) -> list[int]:
        """Парсит admin_ids из строки в список int"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        """URL для подключения к PostgreSQL через asyncpg"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


# глобальный экземпляр настроек
settings = Settings()
