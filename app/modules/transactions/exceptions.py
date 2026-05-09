from app.common.exceptions.exceptions import RouterError


class TrnRouterError(RouterError):
    status_code: int = 400
    detail: str = 'Transaction router error'


class InvalidFieldError(TrnRouterError):
    status_code: int = 400
    detail: str = 'Invalid field error'


class TrnNotFoundError(TrnRouterError):
    status_code: int = 404
    detail: str = 'Transaction not found error'


class TrnCreateError(TrnRouterError):
    status_code: int = 400
    detail: str = 'Transaction create error'


class TrnCurrenciesIsTheSameError(TrnRouterError):
    status_code: int = 409
    detail: str = 'Transaction from_currency == to_currency error'
