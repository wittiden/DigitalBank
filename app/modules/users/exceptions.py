class AppError(Exception):
    status_code: int = 400
    detail: str = 'Application error'


class UserNotFoundError(AppError):
    status_code: int = 404
    detail: str = 'User not Found'


class InvalidFieldError(AppError):
    status_code: int = 400
    detail: str = 'Invalid user field'


class UserEmailIsExistError(AppError):
    status_code: int = 409
    detail: str = 'User email already exist'


class UserPassNotVerifiedError(AppError):
    status_code: int = 401
    detail: str = 'User password not verified'


class UserIsBlockedError(AppError):
    status_code: int = 409
    detail: str = 'User already blocked'


class UserIsNotBlockedError(AppError):
    status_code: int = 409
    detail: str = 'User already unblocked'
