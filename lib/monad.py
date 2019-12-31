#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.4a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'


from .util import foldr


# Look, Ma! It's a monad!
def unit(v):
    yield v

def bind(m, gen):
    return lambda v: (u for w in m(v) for u in gen(w))

def either(*gens):
    return lambda v: (u for gen in gens for u in gen(v))

def and_then(*gens):
    return foldr(bind, gens, unit)

def nothing(_):
    yield from ()

def never(gen):
    def _(v):
        for each in gen(v):
            return nothing(v)
        return unit(v)
    return _


