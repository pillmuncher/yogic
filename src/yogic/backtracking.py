# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

from functools import reduce
from itertools import chain
from collections.abc import Iterable
from typing import Callable, Sequence, TypeVar


# A monad for backtracking. Hence it's called the Backtracking Monad.
# Actually, it's just the Continuation Monad wrapped around the List Monad.


# The naming convention follows the mathematical notation. Therefor:
# pylint: disable=C0103


Value = TypeVar('Value')

Result = Iterable[Value]
Cont = Callable[[Value], Result]
Ma = Callable[[Cont], Result]
Mf = Callable[[Value], Ma]


def bind(ma: Ma, mf: Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    return lambda c: ma(lambda v: mf(v)(c))


def unit(v: Value) -> Ma:
    '''Take the single value v into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid.'''
    return lambda c: c(v)


def zero(v: Value) -> Ma:  # pylint: disable=W0613
    '''Ignore the value v and return an 'empty' monad. Represents failure.'''
    return lambda c: ()


def no(mf: Mf) -> Mf:
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    def _(v: Value):
        def __(c: Cont):
            for result in mf(v)(c):  # pylint: disable=W0612
                # If at least one solution is found, fail immediately:
                return zero(v)(c)
            else:  # pylint: disable=W0120
                # If no solution is found, succeed:
                return unit(v)(c)
        return __
    return _


def then(mf: Mf, mg: Mf) -> Mf:
    '''Apply two monadic functions mf and mg in sequence.
    Together with 'unit', this makes the monad also a monoid.'''
    return lambda v: bind(mf(v), mg)


def _seq_from_iterable(mfs: Sequence[Mf]) -> Mf:
    '''Find solutions matching all mfs.'''
    return reduce(then, mfs, unit)  # type: ignore


def seq(*mfs: Mf) -> Mf:
    '''Find solutions matching all mfs.'''
    return _seq_from_iterable(mfs)

seq.from_iterable = _seq_from_iterable  # type: ignore


def _alt_from_iterable(mfs: Sequence[Mf]) -> Mf:
    '''Find solutions matching any one of mfs.'''
    return lambda v: lambda c: chain.from_iterable(mf(v)(c) for mf in mfs)


def alt(*mfs: Mf) -> Mf:
    '''Find solutions matching any one of mfs.'''
    return _alt_from_iterable(mfs)

alt.from_iterable = _alt_from_iterable  # type: ignore


def run(ma: Ma) -> Result:
    '''Start the monadic computation of ma.'''
    return ma(lambda v: (yield v))  # type: ignore

