from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RefreshTokenModel(Base):
    """Модель хранящая данные долгосрочного токена"""

    __tablename__ = 'refresh_tokens'

    refresh_token_id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return (
            f'refresh_token_id: {self.refresh_token_id}, '
            f'user_id: {self.user_id}, '
            f'expires_at: {self.expires_at}, '
            f'created_at: {self.created_at}, '
            f'revoked_at: {self.revoked_at}, '
            f'version: {self.version}'
        )
