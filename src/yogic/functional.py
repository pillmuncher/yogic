# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''
Provides functional programming utilities for Python, including functions for
flipping argument order and performing a right fold operation on iterables.
'''

from collections.abc import Iterable
from functools import wraps, reduce as foldl
from typing import Callable, TypeVar


Value = TypeVar('Value')


Join = Callable[[Value, Value], Value]


def flip(f:Callable[..., Value]) -> Callable[..., Value]:
    '''
    Decorator function to flip the argument order of a given function.

    Parameters:
        f (Callable[..., Value]): The function to be flipped.

    Returns:
        Callable[..., Value]: A new function that takes the reversed arguments
        and calls the original function.
    '''
    @wraps(f)
    def flipped(*args):
        return f(*reversed(args))
    return flipped


def foldr(f:Join, elems:Iterable[Value], end:Value) -> Value:
    '''
    Performs a right fold operation on the given iterable.

    The function applies the binary operator `f` cumulatively from right to
    left to the elements of the iterable `elems`, reducing it to a single value.

    Parameters:
        f (Join): The binary operator function to be applied during folding.
        elems (Iterable[Value]): The iterable to be folded from right to left.
        end (Value): The initial value for the fold operation.

    Returns:
        Value: The final result of the right fold operation.
    '''
    return foldl(flip(f), reversed(tuple(elems)), end)
