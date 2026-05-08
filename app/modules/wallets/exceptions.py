class WalletRouterError(Exception):
    status_code: int = 400
    detail: str = 'Wallet router error'


class InvalidFieldError(WalletRouterError):
    status_code = 400
    detail = 'Invalid wallet field'


class WalletCreateError(WalletRouterError):
    status_code = 400
    detail = 'Error while wallet created'


class WalletNotFoundError(WalletRouterError):
    status_code = 404
    detail = 'Wallet not found'


class WalletIsBlockedError(WalletRouterError):
    status_code = 409
    detail = 'Wallet already blocked'


class WalletIsNotBlockedError(WalletRouterError):
    status_code = 409
    detail = 'Wallet already unblocked'


class WalletPinNotVerifiedError(WalletRouterError):
    status_code = 401
    detail = 'Wallet pin not verified'


class WalletLimitError(WalletRouterError):
    status_code = 403
    detail = 'Wallet count limit'


class WalletPinsIsTheSame(WalletRouterError):
    status_code = 400
    detail = 'Wallet old_pin == new_pin'
