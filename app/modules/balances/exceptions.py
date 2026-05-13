from app.common.exceptions.exceptions import RouterError


class BalanceRouterError(RouterError):
    status_code = 400
    detail = 'Balance router error'


class CreateBalanceError(BalanceRouterError):
    status_code = 400
    detail = 'Create balance error'


class InvalidFieldError(BalanceRouterError):
    status_code = 400
    detail = 'Invalid fild error'


class BalanceCurrencyIsExistError(BalanceRouterError):
    status_code = 409
    detail = 'Balance currency is exist error'


class BalanceNotFoundError(BalanceRouterError):
    status_code = 404
    detail = 'Balance not found error'


class BalanceIsFrozenError(BalanceRouterError):
    status_code = 409
    detail = 'Balance already frozen error'


class BalanceIsNotFrozenError(BalanceRouterError):
    status_code = 409
    detail = 'Balance already unfrozen error'


class BalanceAmountIsNotZeroError(BalanceRouterError):
    status_code = 409
    detail = 'Balance amount is not zero error'


class BalanceLimitError(BalanceRouterError):
    status_code = 409
    detail = 'Balance count limit error'


class BalanceCurrencyNotFoundError(BalanceRouterError):
    status_code = 404
    detail = 'Balance currency not found error'


class BalanceAmountIsLowerError(BalanceRouterError):
    status_code = 409
    detail = 'Balance amount lower than transaction amount'
