# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.19a'
__date__ = '2021-04-15'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'bind',
    'unit',
    'zero',
    'no',
    'alt',
    'seq',
    'run',
    'recursive',
)

from itertools import chain
from functools import wraps

from .utils import foldr


# Look, Ma! It's a Monad!
#
# A monad for backtracking. Hence it's called the Backtracking Monad.
# Actually, it's just the Continuation Monad wrapped around the List Monad.
# Don't tell anyone. Mum's the word.


def bind(ma, mf):
    'Return the result of flatmapping mf over ma.'
    return lambda c: ma(lambda v: mf(v)(c))


def unit(v):
    'Take the single value v into the monad. Represents success.'
    return lambda c: c(v)


def zero(v):
    'Ignore the value v and return an "empty" monad. Represents failure.'
    return lambda c: ()


def no(mf):
    'Invert the result of a monadic computation, AKA negation as failure.'
    def _(v):
        def __(c):
            for result in mf(v)(c):
                # If at least one solution is found, fail immediately:
                return zero(v)(c)
            else:
                # If no solution is found, succeed:
                return unit(v)(c)
        return __
    return _


def alt(*mfs):
    'Find solutions matching any one of mfs.'
    return lambda v: lambda c: chain.from_iterable(mf(v)(c) for mf in mfs)


def seq(*mfs):
    'Find solutions matching all mfs.'
    return foldr(lambda mf, mg: lambda v: bind(mf(v), mg), mfs, start=unit)


def run(ma):
    'Start the monadic computation of ma.'
    return ma(lambda v: (yield v))


def recursive(genfunc):
    'Helper decorator for recursive monadic generator functions.'
    @wraps(genfunc)
    def _(*args, **kwargs):
        return lambda v: genfunc(*args, **kwargs)(v)
    return _
