from typing import TYPE_CHECKING

from app.modules.balances.exceptions import BalanceNotFoundError, BalanceLimitError, BalanceIsFrozenError, \
    BalanceIsNotFrozenError

if TYPE_CHECKING:
    from app.database.models import BalanceModel


class BalanceGuards:
    """Класс для хранения бизнес правил балансов"""

    @staticmethod
    def require_balance_exist(obj: 'BalanceModel'):
        if not obj:
            raise BalanceNotFoundError('Balance not found')

    @staticmethod
    def require_balance_limit(balance_count: int):
        if balance_count >= 4:
            raise BalanceLimitError('Balance limit error (max limit = 3)')

    @staticmethod
    def require_balance_not_frozen(obj: 'BalanceModel'):
        if obj.is_frozen:
            raise BalanceIsFrozenError('Balance is frozen')

    @staticmethod
    def require_balance_not_unfrozen(obj: 'BalanceModel'):
        if not obj.is_frozen:
            raise BalanceIsNotFrozenError('Balance is unfrozen')
