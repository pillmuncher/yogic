#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.16a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'alt',
    'bind',
    'no',
    'both',
    'recursive',
    'run',
    'seq',
    'unit',
    'fail',
)

from itertools import chain
from functools import wraps, reduce

from . import foldr


def bind(ma, mf):
    'Returns the result of flatmapping mf over ma.'
    return lambda y, n, p: ma(lambda v: mf(v)(y, n, p), n, p)


def unit(v):
    'Takes the single value v into the monad. Represents success.'
    return lambda y, n, p: y(v)


def fail(v):
    'Ignores value v and returns an "empty" monad. Represents failure.'
    return lambda y, n, p: n(v)


def plus(ma, mb):
    'Returns the values of both ma and mb.'
    return lambda y, n, p: chain(ma(y, n, p), mb(y, n, p))


def both(mf, mg):
    'Returns a function of a value v that applies both mf and mg to that value.'
    return lambda v: plus(mf(v), mg(v))


def seq(*mfs):
    'Generalizes "bind" to operate on any number of monadic functions.'
    return lambda v: reduce(bind, mfs, unit(v))


def const(v):
    return lambda _: v


def alt(*mfs):
    'Generalizes "both" to operate on any number of monadic functions.'
    return lambda v: reduce(both, mfs, fail)(v)


def amb(*vs):
    return seq(alt(*vs), cut)


def no(mf):
    'Inverts the result of a monadic computation, AKA negation as failure.'
    def _(v):
        def __(y, n, p):
            for each in mf(v)(y, n, p):
                # If at least one solution is found, fail immediately:
                return fail(v)(y, n, p)
            else:
                # If no solution is found, succeed:
                return unit(v)(y, n, p)
        return __
    return _


# def no(mf):
    # return alt(seq(mf, cut, fail), unit)


def cut(v):
    return lambda y, n, p: chain(y(v), p(v))


def once(v):
    yield v


def never(v):
    yield from ()


def run(ma, y=once, n=never, p=never):
    return ma(y, n, p)


def recursive(genfunc):
    'Helper decorator for recursive monadic generator functions.'
    @wraps(genfunc)
    def _(*args):
        return lambda v: genfunc(*args)(v)
    return _
