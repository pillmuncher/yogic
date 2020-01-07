#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.6a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'alt',
    'bind',
    'never',
    'no',
    'once',
    'recursive',
    'run',
    'seq',
    'unit',
    'zero',


from itertools import chain
from functools import wraps, partial

from . import flatmap, foldr, identity


def unit(g):
    return lambda s: lambda c: c(g(s))

def bind(ma, mf):
    return lambda s: lambda c: ma(s)(partial(flatmap, lambda t: mf(t)(c)))

def zero(g):
    return lambda s: lambda c: iter(())

def plus(ma, mb):
    return lambda s: lambda c: chain(ma(s)(c), mb(s)(c))

nothing = lambda c: c(iter(()))
never = lambda s: nothing
once = lambda s: unit(iter)([s])

def seq(*mfs):
    return foldr(bind, mfs, start=once)

def alt(*mfs):
    return foldr(plus, mfs, start=never)

def no(ma):
    def __(s):
        def _(c):
            for each in ma(s)(c):
                return nothing(c)
            else:
                return once(s)(c)
        return _
    return __


def recursive(genfunc):
    @wraps(genfunc)
    def _(*args):
        return lambda s: lambda c: genfunc(*args)(s)(c)
    return _


def run(actions, s, c=identity):
    return actions(s)(c)
