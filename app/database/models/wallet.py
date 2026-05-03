from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Enum, Index, String
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums.wallet_enums import WalletTypesEnum
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import UserModel
    from app.database.models.balance import BalanceModel


class WalletModel(Base):
    """Модель для хранения данных кошельков в бд"""

    __tablename__ = 'wallets'
    __table_args__ = (
        Index('user_id_index', 'user_id'),
    )

    wallet_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    address: Mapped[str] = mapped_column(String(26), default=lambda: uuid4().hex[:26], nullable=False, unique=True)
    pin_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    wallet_type: Mapped[WalletTypesEnum] = mapped_column(Enum(WalletTypesEnum, name='wallet_types_enum'), default=WalletTypesEnum.UNKNOWN, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    owner: Mapped['UserModel'] = relationship('UserModel', back_populates='wallets')
    balances: Mapped[list['BalanceModel']] = relationship('BalanceModel', back_populates='wallet', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return (f'wallet_id: {self.wallet_id} -> user_id: {self.user_id},'
                f' address: {self.address},'
                f' is_blocked: {self.is_blocked},'
                f' type: {self.wallet_type}')
