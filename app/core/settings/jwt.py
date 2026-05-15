from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    """Настройки для работы с jwt токенами"""

    ACCESS_PUBLIC_KEY_PATH: Path
    ACCESS_PRIVATE_KEY_PATH: Path
    ACCESS_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    REFRESH_PRIVATE_KEY_PATH: Path
    REFRESH_PUBLIC_KEY_PATH: Path
    REFRESH_ALGORITHM: str
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_VERSION: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')
