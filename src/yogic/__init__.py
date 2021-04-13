#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (c) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.18a'
__date__ = '2020-04-13'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'flip',
    'foldl',
    'foldr',
    'multimethod',
)

from collections import defaultdict
from functools import wraps, reduce
from inspect import signature, Signature


def flip(f):
    @wraps(f)
    def flipped(*xs):
        return f(*reversed(xs))
    return flipped


SENTINEL = object()


def foldl(f, xs, *, start=SENTINEL):
    xs = tuple(xs)
    if start is SENTINEL:
        return reduce(f, xs)
    else:
        return reduce(f, xs, start)


def foldr(f, xs, *, start=SENTINEL):
    xs = tuple(xs)
    if start is SENTINEL:
        return reduce(flip(f), reversed(xs))
    else:
        return reduce(flip(f), reversed(xs), start)


def multimethod(function, *, _registry=defaultdict(list)):
    '''Provide multimethods to Python, similar to:
    https://www.artima.com/weblogs/viewpost.jsp?thread=101605'''
    _registry[function.__name__].append((
        function,
        tuple(object if sig.annotation is Signature.empty else sig.annotation
              for sig in signature(function).parameters.values())))
    @wraps(function)
    def _(*args, **kwargs):
        for func, types in _registry[function.__name__]:
            if len(args) == len(types):
                if all(map(isinstance, args, types)):
                    return func(*args, **kwargs)
        raise TypeError("multimethod couldn't find matching function!")
    return _
