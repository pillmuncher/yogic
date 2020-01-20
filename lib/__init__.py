#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.16a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'multimethod',
)

from functools import wraps
from inspect import signature, Signature


def multimethod(function):
    '''Provide multimethods to Python, similar to:
    https://www.artima.com/weblogs/viewpost.jsp?thread=101605'''
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
                if all(map(isinstance, args, types)):
                    return function(*args)
        raise TypeError("multimethod couldn't find matching function!")
    return call

multimethod._registry = {}
