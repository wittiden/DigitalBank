from typing import TYPE_CHECKING

from app.modules.wallets.exceptions import WalletNotFoundError, WalletIsBlockedError, WalletIsNotBlockedError, \
    WalletLimitError, WalletPinNotVerifiedError
from app.modules.wallets.service.utils import verify_pin

if TYPE_CHECKING:
    from app.database.models import WalletModel


class WalletGuards:
    """Класс для хранения бизнес правил кошельков"""

    @staticmethod
    def require_wallet_exists(obj: 'WalletModel') -> None:
        if not obj:
            raise WalletNotFoundError('Wallet not found')

    @staticmethod
    def require_wallet_not_blocked(obj: 'WalletModel') -> None:
        if obj.is_blocked:
            raise WalletIsBlockedError('User is blocked')

    @staticmethod
    def require_wallet_not_unblocked(obj: 'WalletModel') -> None:
        if not obj.is_blocked:
            raise WalletIsNotBlockedError('User is unblocked')

    @staticmethod
    def require_wallet_limit(wallets_count: int) -> None:
        if wallets_count >= 6:
            raise WalletLimitError('Wallet limit error (max limit = 5)')

    @staticmethod
    def require_verify_pin(pin: str, pin_hash: str) -> None:
        if not verify_pin(pin, pin_hash):
            raise WalletPinNotVerifiedError('Wallet pin not verified')
