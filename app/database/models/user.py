from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums.user_enums import UserStatusesEnum
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.wallet import WalletModel


class UserModel(Base):
    """Модель для хранения данных пользователей в бд"""

    __tablename__ = 'users'

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    user_status: Mapped[UserStatusesEnum] = mapped_column(Enum(UserStatusesEnum, name='user_statuses_enum'), default=UserStatusesEnum.UNKNOWN, nullable=False)

    wallets: Mapped[list['WalletModel']] = relationship('WalletModel', back_populates='owner', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'user_id: {self.user_id}, name: {self.name}, email: {self.email}, is_blocked: {self.is_blocked}, status: {self.user_status}'
