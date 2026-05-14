from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums.transaction_enums import TransactionStatusesEnum, TransactionTypesEnum
from app.database.base import Base


class TransactionModel(Base):
    """Модель для хранения данных транзакций в бд"""

    __tablename__ = 'transactions'

    transaction_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    from_address: Mapped[str] = mapped_column(String(26), ForeignKey('wallets.address'), nullable=False)
    to_address: Mapped[str] = mapped_column(String(26), ForeignKey('wallets.address'), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    from_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    to_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    transaction_type: Mapped[TransactionTypesEnum] = mapped_column(Enum(TransactionTypesEnum, name='transaction_types_enum'), default=TransactionTypesEnum.UNKNOWN, nullable=False)
    transaction_status: Mapped[TransactionStatusesEnum] = mapped_column(
        Enum(TransactionStatusesEnum, name='transaction_statuses_enum'), default=TransactionStatusesEnum.UNKNOWN, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f'transaction_id: {self.transaction_id},'
            f' from_wallet_id: {self.from_address},'
            f' to_wallet_id: {self.to_address},'
            f' amount: {self.amount},'
            f' fee: {self.fee},'
            f' rate: {self.rate}, '
            f'started_at: {self.started_at},'
            f' completed_at: {self.completed_at},'
            f' from_currency: {self.from_currency},'
            f' to_currency: {self.to_currency},'
            f' type: {self.transaction_type}, '
            f'status: {self.transaction_status}'
        )
