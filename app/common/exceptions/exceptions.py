class RouterError(Exception):
    status_code: int = 400
    detail: str = 'Router error'
