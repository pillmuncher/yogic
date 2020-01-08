#!/usr/bin/env python3
# coding: utf-8
#
# Copyright  2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.8a'
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
    'run',
    'seq',
    'unit',
    'zero',
)

from itertools import chain
from functools import wraps, partial, reduce


# Look, Ma! It's a Monad!
#
# A monad for backtracking. Hence it's called the Backtracking Monad.


def amb(*vs):
    '''Take the sequence vs of values into the monad.'''
    return iter(vs)


def unit(v):
    '''Take the single value v into the monad. Monadic 1.
    Represents success.'''
    return amb(v)


def zero(v):
    '''Ignore value v and return an "empty" monad. Monadic 0.
    Represents failure.'''
    return amb()


def bind(mf, mg):
    '''The monadic bind operation, AKA monadic multiplication.
    Filter the results of mf through mg.'''
    return lambda v: (u for w in mf(v) for u in mg(w))


def plus(mf, mg):
    '''The monadic plus operation, AKA monadic addition.
     Generate a sequence from the results of both mf and mg.'''
    return lambda v: chain(mf(v), mg(v))


def seq(*mfs):
    '''Generalize bind to operate on any number of monadic functions.'''
    return reduce(bind, mfs, unit)


def alt(*mfs):
    '''Generalize plus to operate on any number of monadic functions.'''
    return reduce(plus, mfs, zero)


def no(mf):
    '''Reverse the result of a monadic computation, AKA negation as failure.'''
    def __(v):
            for each in mf(v):
                return zero(v)
            else:
                return unit(v)
    return __


def recursive(genfunc):
    '''Helper decorator for recursive predicate functions.'''
    @wraps(genfunc)
    def _(*args):
        return lambda v: genfunc(*args)(v)
    return _


def run(actions, v):
    '''Start a monadic computation.
     Returns all transformations of value v as defined by "actions".'''
    return actions(v)
