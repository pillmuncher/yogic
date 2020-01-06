#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <ma.krippendorf@freenet.de>

__version__ = '0.6a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <ma.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'alt',
    'bind',
    'cut',
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

from .. import comp, identity, foldr
from . import generator as gen
from . import continuation as cont


def mflip(f):
    return lambda x: lambda y: f(y)(x)

# Look, Ma! It's a monad!
def bind(ma, mf):
    return cont.bind(ma, lambda g: lambda c: gen.bind(g, mf(c)))

unit = comp(gen.unit, cont.unit)
zero = mflip(comp(gen.zero, cont.unit))
nothing = cont.unit(gen.nothing)

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
