#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.6a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # export from here
    'resolve',
    'unify',
    'var',
    # re-export from lib.monad.backtracking
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

from collections import namedtuple, ChainMap
from itertools import count, starmap

from . import multimethod
from .backtracking import (
    alt, bind, never, no, nothing, once, plus, recursive, run, seq, unit, zero
)


Variable = namedtuple('Variable', 'id')
Variable._counter = count()

def var():
    return Variable(next(Variable._counter))


class Subst(ChainMap):
    @property
    class proxy:
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return chase(var, self._subst, True)


def resolve(goal):
    return (subst.proxy for subst in run(goal, Subst()))


@multimethod
def chase(v: Variable, subst: Subst, deep):
    if v in subst:
        return chase(subst[v], subst, deep)
    else:
        return v

@multimethod
def chase(o: (list, tuple), subst: Subst, deep):
    if deep:
        return type(o)(map(lambda x: chase(x, subst, True), o))
    else:
        return o

@multimethod
def chase(o: object, subst: Subst, deep):
    return o


@multimethod
def _unify(this: Variable, that: object):
    if this == that:
        return once
    else:
        return lambda s: once(s.new_child({this: that}))

@multimethod
def _unify(this: object, that: Variable):
    return _unify(that, this)

@multimethod
def _unify(this: (list, tuple), that: (list, tuple)):
    if type(this) == type(that) and len(this) == len(that):
        return seq(*starmap(unify, zip(this, that)))
    else:
        return never

@multimethod
def _unify(this: object, that: object):
    if this == that:
        return once
    else:
        return never


def unify(this, that):
    return lambda s: _unify(chase(this, s, False), chase(that, s, False))(s)
