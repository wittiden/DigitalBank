import functools
from collections.abc import Awaitable, Callable
from typing import Concatenate, ParamSpec, TypeVar

from loguru import logger

T = TypeVar('T')
Self = TypeVar('Self')
P = ParamSpec('P')


def debug_log[Self, **P, T](func: Callable[Concatenate[Self, P], Awaitable[T]]) -> Callable[Concatenate[Self, P], Awaitable[T]]:
    @functools.wraps(func)
    async def wrapped(self: Self, *args: P.args, **kwargs: P.kwargs) -> T:

        logger.debug('Strat - {}', func.__name__)

        result = await func(self, *args, **kwargs)

        logger.debug('End - {}', func.__name__)

        return result

    return wrapped
