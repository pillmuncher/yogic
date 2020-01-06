#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <ma.krippendorf@freenet.de>

__version__ = '0.6a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <ma.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'bind',
    'callcc',
    'cont',
    'plus',
    'unit',
    'zero',
)

from functools import wraps


def bind(ma, mf):
    return lambda c: ma(lambda s: mf(s)(c))

def unit(s):
    return lambda c: c(s)

def zero(s):
    return lambda c: None

def plus(ma, mb):
    return lambda c: lambda s: bind(ma(s), mb)(c)

def callcc(cc):
    return lambda c: cc(lambda s: lambda _: c(s))(c)

def cont(f):
    @wraps(f)
    def _(*args, **kwargs):
        return f(*args, **kwargs)
    return _
