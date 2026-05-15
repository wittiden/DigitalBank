from app.common.exceptions.exceptions import RouterError


class AuthRouterError(RouterError):
    status_code = 400
    detail = 'Auth router error'


class InvalidFieldError(AuthRouterError):
    status_code = 400
    detail = 'Invalid field error'


class ForbiddenError(AuthRouterError):
    status_code = 403
    detail = 'Not enough permissions'


class UserPassNotVerifiedError(AuthRouterError):
    status_code: int = 401
    detail: str = 'User password not verified error'


class UserIsBlockedError(AuthRouterError):
    status_code: int = 403
    detail: str = 'User is blocked error'


class TokenInvalidError(AuthRouterError):
    status_code = 400
    detail = 'Token invalid error'


class RevokedTokenError(AuthRouterError):
    status_code = 401
    detail = 'Revoked token error'


class OldTokenError(AuthRouterError):
    status_code = 401
    detail = 'Old token error'


class RefreshTokenNotFoundError(AuthRouterError):
    status_code = 404
    detail = 'Refresh token not found error'
