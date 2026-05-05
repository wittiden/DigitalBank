class WalletRouterError(Exception):
    status_code: int = 400
    detail: str = 'Wallet router error'


class InvalidFieldError(WalletRouterError):
    status_code = 400
    detail = 'Invalid wallet field'


class WalletCreateError(WalletRouterError):
    pass


class WalletNotFoundError(WalletRouterError):
    pass


class WalletIsBlockedError(WalletRouterError):
    pass


class WalletIsNotBlockedError(WalletRouterError):
    pass


class WalletPinNotVerifiedError(WalletRouterError):
    pass


class WalletLimitError(WalletRouterError):
    pass
