#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.7a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'alt',
    'bind',
    'never',
    'no',
    'nothing',
    'once',
    'plus',
    'recursive',
    'run',
    'seq',
    'unit',
    'zero',
)

from itertools import chain, repeat
from functools import wraps, partial

from . import flatmap, foldr, identity


# Look, Ma! It's a Monad!

def unit(g):
    return lambda v: lambda c: c(g(v))


def bind(ma, mf):
    return lambda v: lambda c: ma(v)(partial(flatmap, lambda u: mf(u)(c)))


def zero(g):
    return lambda v: lambda c: c(iter(()))


def plus(ma, mb):
    return lambda v: lambda c: chain(ma(v)(c), mb(v)(c))


once = lambda v: lambda c: c(repeat(v, 1))
never = zero(None)
nothing = never(None)


def seq(*mfs):
    return foldr(bind, mfs, start=once)


def alt(*mfs):
    return foldr(plus, mfs, start=never)


def no(ma):
    def __(v):
        def _(c):
            for each in ma(v)(c):
                return nothing(c)
            else:
                return once(v)(c)
        return _
    return __


def recursive(genfunc):
    @wraps(genfunc)
    def _(*args):
        return lambda v: lambda c: genfunc(*args)(v)(c)
    return _


def run(actions, v, c=identity):
    return actions(v)(c)
