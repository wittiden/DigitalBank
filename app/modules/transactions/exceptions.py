class TrnRouterError(Exception):
    status_code: int = 400
    detail: str = ''


class InvalidFieldError(TrnRouterError):
    pass


class TrnNotFoundError(TrnRouterError):
    pass


class TrnCreateError(TrnRouterError):
    pass


class TrnCurrenciesIsTheSameError(TrnRouterError):
    pass