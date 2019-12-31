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
    'cut',
    'never',
    'nothing',
    'recursive',
    'seq',
    'unit',
)

from .util import foldr


# Look, Ma! It's a monad!
def unit(v):
    yield v

def bind(m, gen):
    return lambda v: (u for w in m(v) for u in gen(w))

def alt(*gens):
    return lambda v: (u for gen in gens for u in gen(v))

def seq(*gens):
    return foldr(bind, gens, unit)

def nothing(_):
    yield from ()

def never(gen):
    def _(v):
        for each in gen(v):
            return nothing(v)
        return unit(v)
    return _

def cut(v):  # TODO: make it work
    yield v

def recursive(genfunc):
    @wraps(genfunc)
    def __(*args):
        def _(v):
            return (u for u in genfunc(*args)(v))
        return _
    return __
