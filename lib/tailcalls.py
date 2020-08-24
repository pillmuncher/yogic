#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.16a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'bind',
    'unit',
    'fail',
    'both',
    'callcc',
    'cont',
)

from functools import partial


def unit(*args, **kwargs):
    return lambda v: lambda c: c, v, args, kwargs


def fail(*args, **kwargs):
    return lambda v: lambda c: None, (), args, kwargs


def emit(cont, *args, _=None, **kwargs):
    return cont, [_], args, kwargs


def abort(*args, **kwargs):
    return None, (), args, kwargs


def bounce(cont, *args, **kwargs):
    return cont, (), args, kwargs


def tailcall(function):
    return partial(bounce, function)


def trampoline(bouncing, *args, **kwargs):
    while bouncing:
        bouncing, result, args, kwargs = bouncing(*args, **kwargs)
        yield from result
