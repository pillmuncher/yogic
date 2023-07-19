# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''xxx'''

from collections.abc import Iterable
from functools import wraps, reduce as foldl
from typing import Callable, TypeVar


Value = TypeVar('Value')


Join = Callable[[Value, Value], Value]


def flip(f:Callable[..., Value]) -> Callable[..., Value]:
    '''Flip the order of arguments with which a function is called.'''
    @wraps(f)
    def flipped(*args):
        return f(*reversed(args))
    return flipped


def foldr(f:Join, elems:Iterable[Value], end:Value) -> Value:
    '''Right associative reduce.'''
    return foldl(flip(f), reversed(tuple(elems)), end)
