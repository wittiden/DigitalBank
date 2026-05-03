from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index, Enum, String, Numeric, ForeignKey
from uuid import UUID, uuid4

from app.common.enums.balance_enums import BalanceTypesEnum
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.wallet import WalletModel


class BalanceModel(Base):
    """Модель для хранения данных балансов в бд"""

    __tablename__ = 'balances'
    __table_args__ = (
        Index('wallet_id_index', 'wallet_id'),
    )

    balance_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal('0.00'), nullable=False)
    is_frozen: Mapped[bool] = mapped_column(default=False, nullable=False)
    balance_type: Mapped[BalanceTypesEnum] = mapped_column(Enum(BalanceTypesEnum, name='balance_types_enum'), default=BalanceTypesEnum.UNKNOWN, nullable=False)
    wallet_id: Mapped[UUID] = mapped_column(ForeignKey('wallets.wallet_id', ondelete='CASCADE'), nullable=False)

    wallet: Mapped['WalletModel'] = relationship('WalletModel', back_populates='balances')

    def __repr__(self) -> str:
        return (f'balance_id: {self.balance_id} -> wallet_id: {self.wallet_id},'
                f'currency: {self.currency},'
                f'amount: {self.amount},'
                f'is_frozen: {self.is_frozen},'
                f'type: {self.balance_type}')
