from typing import TYPE_CHECKING

from app.modules.transactions.exceptions import TrnNotFoundError

if TYPE_CHECKING:
    from app.database.models import TransactionModel


class TrnGuards:
    """Класс для хранения бизнес правил транзакций"""

    @staticmethod
    def require_trn_exist(obj: 'TransactionModel'):
        if not obj:
            raise TrnNotFoundError('Transaction not found')
