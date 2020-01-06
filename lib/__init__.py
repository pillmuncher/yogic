#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.5a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'comp',
    'const',
    'flatmap',
    'flip',
    'foldr',
    'identity',
    'multimethod',
)

from functools import wraps, reduce
from itertools import starmap, chain
from inspect import signature, Signature


SENTINEL = object()

def foldr(f, xs, *, start=SENTINEL):
    if start is SENTINEL:
        return reduce(flip(f), reversed(xs))
    else:
        return reduce(flip(f), reversed(xs), start)

def flatmap(f, i):
    return chain.from_iterable(map(f, i))

def identity(x):
    "The I combinator"
    return x

def const(x):
    "The K combinator"
    return lambda _: x

def flip(f):
    return lambda x, y: f(y, x)

def comp(f, g):
    return lambda x: g(f(x))


def multimethod(function):
    typemap = multimethod._registry.setdefault(function.__name__, [])
    typemap.append((
        function,
        tuple(
            object if each.annotation is Signature.empty else each.annotation
            for each in signature(function).parameters.values())))
    @wraps(function)
    def call(*args):
        for function, types in typemap:
            if len(args) == len(types):
                if all(starmap(isinstance, zip(args, types))):
                    return function(*args)
        raise TypeError("multimethod couldn't find matching function!")
    return call

multimethod._registry = {}
