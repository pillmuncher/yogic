#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.5a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'flip',
    'foldr',
    'multimethod',
)

from functools import wraps, reduce
from itertools import starmap
from inspect import signature, Signature


def flip(f):
    return lambda x, y: f(y, x)


def foldr(f, xs, x):
    return reduce(flip(f), reversed(xs), x)


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
