from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    """Настройки для работы с jwt токенами"""

    PUBLIC_KEY_PATH: Path
    PRIVATE_KEY_PATH: Path
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')
