from app.database.models import BalanceModel
from app.modules.balances.exceptions import BalanceIsFrozenError, BalanceLimitError, BalanceNotFoundError


class BalanceGuards:
    """Класс для хранения бизнес правил баланса"""

    @staticmethod
    def require_balance_limit(balance_count: int | None) -> int:
        if balance_count is None:
            balance_count = 0

        if balance_count >= 4:
            raise BalanceLimitError('Balance limit error (max limit = 3)')

        return balance_count

    @staticmethod
    def require_balance_exist(obj: BalanceModel | None) -> BalanceModel:
        if not obj:
            raise BalanceNotFoundError('Balance not found error')

        return obj

    @staticmethod
    def require_balance_not_frozen(obj: BalanceModel):
        if obj.is_frozen:
            raise BalanceIsFrozenError('Balance is frozen error')

    @staticmethod
    def require_balance_not_unfrozen(obj: BalanceModel):
        if not obj.is_frozen:
            raise BalanceIsFrozenError('Balance is frozen error')
