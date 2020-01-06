#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <ma.krippendorf@freenet.de>

__version__ = '0.6a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <ma.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'abort',
    'bounce',
    'emit',
    'tailcall',
    'trampoline',
)

from functools import partial


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
