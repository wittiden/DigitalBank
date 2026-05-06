class BalanceRouterError(Exception):
    status_code = 400
    detail = 'Balance router error'


class InvalidFieldError(BalanceRouterError):
    status_code = 400
    detail = 'Invalid fild error'