class UserNotFoundError(Exception):
    pass


class InvalidFieldError(Exception):
    pass


class UserEmailIsExistError(Exception):
    pass


class UserPassNotVerifiedError(Exception):
    pass


class UserIsBlockedError(Exception):
    pass


class UserIsNotBlockedError(Exception):
    pass
