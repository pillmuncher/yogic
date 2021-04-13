#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (c) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.16a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'bind',
    'unit',
    'fail',
    'seq',
    'alt',
    'no',
    'run',
    'recursive',
)

from itertools import chain
from functools import wraps

from . import foldr


# Look, Ma! It's a Monad!
#
# A monad for backtracking. Hence it's called the Backtracking Monad.
# Actually, it's just the Continuation Monad wrapped aroun the List Monad.
# Don't tell anyone. Mum's the word.


def bind(ma, mf):
    'Returns the result of flatmapping mf over ma.'
    return lambda c: ma(lambda v: mf(v)(c))


def unit(v):
    'Takes the single value v into the monad. Represents success.'
    return lambda c: c(v)


def fail(v):
    'Ignores value v and returns an "empty" monad. Represents failure.'
    return lambda c: never()


def seq(*mfs):
    'Find every solution natching all mfs.'
    return foldr(lambda mf, mg: lambda v: bind(mf(v), mg), mfs, start=unit)


def alt(*mfs):
    'Find every solution matching any one of mfs.'
    return lambda v: lambda c: chain(*(mf(v)(c) for mf in mfs))


def no(mf):
    'Invert the result of a monadic computation, AKA negation as failure.'
    def _(v):
        def __(c):
            for each in mf(v)(c):
                # If at least one solution is found, fail immediately:
                return fail(v)(c)
            else:
                # If no solution is found, succeed:
                return unit(v)(c)
        return __
    return _


def once(v):
    yield v


def never():
    yield from ()


def run(ma):
    'Start the monadic computation of ma.'
    return ma(once)


def recursive(genfunc):
    'Helper decorator for recursive monadic generator functions.'
    @wraps(genfunc)
    def _(*args):
        return lambda v: genfunc(*args)(v)
    return _
