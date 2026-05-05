class WalletRouterError(Exception):
    status_code: int = 400
    detail: str = 'Wallet router error'


class InvalidFieldError(WalletRouterError):
    status_code = 400
    detail = 'Invalid wallet field'