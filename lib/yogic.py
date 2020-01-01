#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.5a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'alt',
    'bind',
    'never',
    'nothing',
    'recursive',
    'resolve',
    'seq',
    'unify',
    'unit',
    'var',
)

from collections import namedtuple, ChainMap
from itertools import count, starmap, repeat

from .util import multimethod
from .monad import alt, bind, cut, never, nothing, recursive, seq, unit


Variable = namedtuple('Variable', 'id')

def var():
    return Variable(next(var._counter))

var._counter = count()


class Subst(ChainMap):
    @property
    class proxy:
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return chase(var, self._subst)


def resolve(goal):
    return (subst.proxy for subst in goal(Subst()))


@multimethod
def chase(v: Variable, subst: Subst):
    if v in subst:
        return chase(subst[v], subst)
    else:
        return v

@multimethod
def chase(o: (list, tuple), subst: Subst):
    return type(o)(map(chase, o, repeat(subst)))

@multimethod
def chase(o: object, subst: Subst):
    return o


@multimethod
def _unify(this: Variable, that: object):
    def _(subst):
        if this == that:
            yield subst
        else:
            yield subst.new_child({this: that})
    return _

@multimethod
def _unify(this: object, that: Variable):
    return _unify(that, this)

@multimethod
def _unify(this: (list, tuple), that: (list, tuple)):
    if type(this) == type(that) and len(this) == len(that):
        return seq(*starmap(unify, zip(this, that)))
    else:
        return nothing

@multimethod
def _unify(this: object, that: object):
    if this == that:
        return unit
    else:
        return nothing

def unify(this, that):
    return lambda s: _unify(chase(this, s), chase(that, s))(s)
