import functools
from loguru import logger
from typing import Callable, TypeVar, ParamSpec, Concatenate, Awaitable

T = TypeVar('T')
Self = TypeVar('Self')
P = ParamSpec('P')


def debug_log(func: Callable[Concatenate[Self, P], Awaitable[T]]) -> Callable[Concatenate[Self, P], Awaitable[T]]:
    @functools.wraps(func)
    async def wrapped(self: Self, *args: P.args, **kwargs: P.kwargs) -> T:

        logger.debug('Strat - {}', func.__name__)

        result = func(self, *args, **kwargs)

        logger.debug('End - {}', func.__name__)

        return result
    return wrapped
