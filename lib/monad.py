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
    'zero',
    'recursive',
    'seq',
    'unit',
)

from functools import partial

from . import flip, flatmap, const, comp, identity, foldr

def trampoline(bouncing, *args, **kwargs):
    while bouncing:
        bouncing, result, args, kwargs = bouncing(*args, **kwargs)
        yield from result

def abort(*args, **kwargs):
    return None, (), args, kwargs

def emit(cont, *args, _=None, **kwargs):
    return cont, [_], args, kwargs

def bounce(cont, *args, **kwargs):
    return cont, (), args, kwargs

def tailcall(function):
    return partial(bounce, function)


# ---8<--------8<--------8<--------8<--------8<--------8<--------8<--------8<---


# Generator Monad:


from itertools import chain


gbind = flip(flatmap)
gunit = iter
gnothing = iter(())
gzero = const(gnothing)
gplus = chain


# ---8<--------8<--------8<--------8<--------8<--------8<--------8<--------8<---


# Continuation Monad:


from functools import wraps


def cbind(ma, mf):
    return lambda c: ma(lambda s: mf(s)(c))

def cunit(s):
    return lambda c: c(s)

def czero(s):
    return lambda c: None

def cplus(ma, mb):
    return lambda c: lambda s: cbind(ma(s), mb)(c)

def callcc(cc):
    return lambda c: cc(lambda s: lambda _: c(s))(c)

def cont(f):
    @wraps(f)
    def _(*args, **kwargs):
        return f(*args, **kwargs)
    return _


# ---8<--------8<--------8<--------8<--------8<--------8<--------8<--------8<---


# Resolver Monad:


from collections import ChainMap


def mflip(f):
    return lambda x: lambda y: f(y)(x)

# Look, Ma! It's a monad!
def bind(ma, mf):
    return cbind(ma, lambda g: lambda c: gbind(g, mf(c)))

unit = comp(gunit, cunit)
zero = mflip(comp(gzero, cunit))
nothing = cunit(gnothing)

@mflip
def once(s):
    return unit(iter([s]))

def plus(ma, mb):
    return lambda c: lambda s: gplus(ma(c)(s), mb(c)(s))

def seq(*gens):
    return foldr(bind, gens, start=once)

def alt(*gens):
    return foldr(plus, gens, start=zero)

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
