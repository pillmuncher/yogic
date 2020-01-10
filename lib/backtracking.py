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
    'plus',
    'recursive',
    'seq',
    'unit',
    'zero',
)

from itertools import chain
from functools import wraps, reduce


# Look, Ma! It's a Monad!
#
# A monad for backtracking. Hence it's called the Backtracking Monad.


def amb(*vs):
    'Takes the sequence vs of values into the monad.'
    return iter(vs)


def unit(v):
    'Takes the single value v into the monad. Represents success.'
    return amb(v)


def zero(v):
    'Ignores value v and returns an "empty" monad. Represents failure.'
    return amb()


def bind(mf, mg):
    'Returns the result of flatmapping mg over mf(v).'
    return lambda v: (u for w in mf(v) for u in mg(w))


def plus(mf, mg):
    'Returns the results of both mf(v) and mg(v).'
    return lambda v: chain(mf(v), mg(v))


def seq(*mfs):
    'Generalizes bind to operate on any number of monadic functions.'
    return reduce(bind, mfs, unit)


def alt(*mfs):
    'Generalizes plus to operate on any number of monadic functions.'
    return reduce(plus, mfs, zero)


def no(mf):
    'Reverses the result of a monadic computation, AKA negation as failure.'
    def _(v):
        for each in mf(v):
            # If at least one solution is found, fail immediately:
            return zero(v)
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
