#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.4a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'


from collections import namedtuple, ChainMap
from functools import singledispatch, wraps
from itertools import count, starmap

from .util import multimethod
from .monad import and_then, bind, either, nothing, unit


Variable = namedtuple('Variable', 'name')

def var():
    return Variable('v' + str(next(var._counter)))

var._counter = count()


class Subst(ChainMap):
    @property
    class proxy:
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return chase(var, self._subst)


def chase(var, subst):
    while var in subst:
        var = subst[var]
    return var


def resolve(goal):
    return (subst.proxy for subst in goal(Subst()))


def recursive(g):
    @wraps(g)
    def __(*args):
        def _(subst):
            return (each for each in g(*args)(subst))
        return _
    return __


def cut(subst):
    yield subst


@multimethod
def _unify(this: Variable, that: object):
    def _(subst):
        yield subst.new_child({this: that})
    return _

@multimethod
def _unify(this: object, that: Variable):
    return _unify(that, this)

@multimethod
def _unify(this: object, that: object):
    return unify(this, that)

@multimethod
def unify(this: Variable, that: Variable):
    return lambda s: _unify(chase(this, s), chase(that, s))(s)

@multimethod
def unify(this: Variable, that: object):
    return lambda s: _unify(chase(this, s), that)(s)

@multimethod
def unify(this: object, that: Variable):
    return lambda s: _unify(this, chase(that, s))(s)

@multimethod
def unify(this: list, that: list):
    if len(this) == len(that):
        return and_then(*starmap(unify, zip(this, that)))
    else:
        return nothing

@multimethod
def unify(this: list, that: object):
    return nothing

@multimethod
def unify(this: object, that: list):
    return nothing

@multimethod
def unify(this: object, that: object):
    if this == that:
        return unit
    else:
        return nothing
