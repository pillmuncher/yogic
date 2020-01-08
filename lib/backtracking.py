#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

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

from . import flatmap, identity


# Look, Ma! It's a Monad!
#
# In essence, it's the Continuation Monad, but applied to Generators and
# Iterators. Therefor the bind operator flatmaps over the computation results,
# thus providing a mechanism for exhaustive search through solutions spaces with
# backtracking. Hence it's called the Backtracking Monad.
#
# I know, it looks a bit like printer vomit, but I promise, it's not all too
# difficult to understand. The abbreviations are these:
#
# v : a value that will be provided as argument to monadic functions.
# c : a continuation that recieves the result of monadic computations.
# mx: a monadic function, taking a value and a continuation into the monad.


def amb(*vs):
    '''Take the sequence vs of values into the monad.'''
    return lambda c: c(iter(vs))


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
    return lambda v: lambda c: mf(v)(partial(flatmap, lambda u: mg(u)(c)))


def plus(mf, mg):
    '''The monadic plus operation, AKA monadic addition.
     Generate a sequence from the results of both mf and mg.'''
    return lambda v: lambda c: chain(mf(v)(c), mg(v)(c))


def seq(*mfs):
    '''Generalize bind to operate on any number of monadic functions.'''
    return reduce(bind, mfs, unit)


def alt(*mfs):
    '''Generalize plus to operate on any number of monadic functions.'''
    return reduce(plus, mfs, zero)


def no(mf):
    '''Reverse the result of a monadic computation, AKA negation as failure.'''
    def __(v):
        def _(c):
            for each in mf(v)(c):
                return zero(v)(c)
            else:
                return unit(v)(c)
        return _
    return __


def recursive(genfunc):
    '''Helper decorator for recursive generator functions.'''
    @wraps(genfunc)
    def _(*args):
        return lambda v: lambda c: genfunc(*args)(v)(c)
    return _


def run(actions, v):
    '''Start a monadic computation.
     Returns all transformations of value v as defined by "actions".'''
    return actions(v)(identity)
