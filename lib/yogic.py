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
    'cut',
    'no',
    'once',
    'recursive',
    'resolve',
    'seq',
    'unify',
    'unit',
    'var',
    'zero',
    # re-export drom lib.monad.continuation:
    'cont',
)

from collections import namedtuple, ChainMap
from itertools import count, starmap, repeat

from . import comp, foldr, identity, multimethod
from .monad import generator as gen
from .monad import continuation as con
from .monad.continuation import cont


def mflip(f):
    return lambda x: lambda y: f(y)(x)

# Look, Ma! It's a monad!
def bind(ma, mf):
    return con.bind(ma, lambda g: lambda c: gen.bind(g, mf(c)))

unit = comp(gen.unit, con.unit)
zero = mflip(comp(gen.zero, con.unit))
nothing = con.unit(gen.nothing)

@mflip
def once(s):
    return unit(iter([s]))

def plus(ma, mb):
    return lambda c: lambda s: gen.plus(ma(c)(s), mb(c)(s))

def seq(*mfs):
    return foldr(bind, mfs, start=once)

def alt(*mfs):
    return foldr(plus, mfs, start=zero)

def no(ma):
    def __(c):
        def _(s):
            for each in ma(c)(s):
                return nothing(c)
            else:
                return once(c)(s)
        return _
    return __

def run(actions, s, c=identity):
    return bind(unit([s]), actions)(c)

def cut(s):  # TODO: make it work
    yield s

def recursive(genfunc):
    def _(*args):
        return lambda c: lambda s: genfunc(*args)(c)(s)
    return _
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
        return lambda c: lambda s: unit(repeat(s.new_child({this: that}), 1))(c)

@multimethod
def _unify(this: object, that: Variable):
    return lambda c: lambda s: unit(repeat(s.new_child({that: this}), 1))(c)

@multimethod
def _unify(this: (list, tuple), that: (list, tuple)):
    if type(this) == type(that) and len(this) == len(that):
        return seq(*starmap(unify, zip(this, that)))
    else:
        return zero

@multimethod
def _unify(this: object, that: object):
    if this == that:
        return once
    else:
        return zero


def unify(this, that):
    return lambda c: lambda s: _unify(
            chase(this, s, False),
            chase(that, s, False))(c)(s)
