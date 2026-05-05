class UserRouterError(Exception):
    status_code: int = 400
    detail: str = 'User router error'


class UserNotFoundError(UserRouterError):
    status_code: int = 404
    detail: str = 'User not Found'


class InvalidFieldError(UserRouterError):
    status_code: int = 400
    detail: str = 'Invalid user field'


class UserEmailIsExistError(UserRouterError):
    status_code: int = 409
    detail: str = 'User email already exist'


class UserPassNotVerifiedError(UserRouterError):
    status_code: int = 401
    detail: str = 'User password not verified'


class UserIsBlockedError(UserRouterError):
    status_code: int = 409
    detail: str = 'User already blocked'


class UserIsNotBlockedError(UserRouterError):
    status_code: int = 409
    detail: str = 'User already unblocked'
