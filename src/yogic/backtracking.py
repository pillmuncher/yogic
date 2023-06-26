# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__all__ = (
    'alt_from_iterable',
    'bind',
    'no',
    'run',
    'seq_from_iterable',
    'alt',
    'seq',
    'unit',
    'zero',
)

from itertools import chain
from functools import reduce


# Look, Ma! It's a Monad!
#
# A monad for backtracking. Hence it's called the Backtracking Monad.
# Actually, it's just the Continuation Monad wrapped around the List Monad.
# Don't tell anyone. Mum's the word.


def bind(ma, mf):
    'Return the result of applying mf to ma.'
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


def then(mf, mg):
    'Apply two monadic functions mf and mg in sequence.'
    'Together with unit, this makes the monad also a monoid.'
    return lambda v: bind(mf(v), mg)


def _seq_from_iterable(mfs):
    'Find solutions matching all mfs.'
    return reduce(then, mfs, unit)


def seq(*mfs):
    'Find solutions matching all mfs.'
    return _seq_from_iterable(mfs)

seq.from_iterable = _seq_from_iterable


def _alt_from_iterable(mfs):
    'Find solutions matching any one of mfs.'
    return lambda v: lambda c: chain.from_iterable(mf(v)(c) for mf in mfs)


def alt(*mfs):
    'Find solutions matching any one of mfs.'
    return _alt_from_iterable(mfs)

alt.from_iterable = _alt_from_iterable


def run(ma):
    'Start the monadic computation of ma.'
    return ma(lambda v: (yield v))
