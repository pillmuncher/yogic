#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.13a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'alt',
    'amb',
    'bind',
    'no',
    'both',
    'recursive',
    'seq',
    'unit',
    'fail',
)

from itertools import chain
from functools import wraps, reduce


# Look, Ma! It's a Monad!
#
# A monad for backtracking. Hence it's called the Backtracking Monad.
# (Actually, it's just the List Monad. Don't tell anyone. Mum's the word.)


def flatmap(f, seq):
    return chain.from_iterable(map(f, seq))


def amb(*vs):
    'Takes the sequence vs of values into the monad.'
    return iter(vs)


def unit(v):
    'Takes the single value v into the monad. Represents success.'
    return amb(v)


def fail(v):
    'Ignores value v and returns an "empty" monad. Represents failure.'
    return amb()


def bind(ma, mf):
    'Returns the result of flatmapping mg over mf(v).'
    return flatmap(mf, ma)


def both(ma, mb):
    'Returns the results of both mf(v) and mg(v).'
    return chain(ma, mb)


def seq(*mfs):
    'Generalizes bind to operate on any number of monadic functions.'
    return lambda v: reduce(bind, mfs, unit(v))


def alt(*mfs):
    'Generalizes both to operate on any number of monadic functions.'
    return lambda v: flatmap(lambda mf: mf(v), mfs)


def no(mf):
    'Inverts the result of a monadic computation, AKA negation as failure.'
    def _(v):
        for each in mf(v):
            # If at least one solution is found, fail immediately:
            return fail(v)
        else:
            # If no solution is found, succeed:
            return unit(v)
    return _


def recursive(genfunc):
    'Helper decorator for recursive monadic generator functions.'
    @wraps(genfunc)
    def _(*args):
        return lambda v: genfunc(*args)(v)
    return _
