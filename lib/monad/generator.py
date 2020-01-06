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
    'nothing',
    'plus',
    'unit',
    'zero',
)

from itertools import chain

from .. import flip, flatmap, const


bind = flip(flatmap)
unit = iter
nothing = iter(())
zero = const(nothing)
plus = chain
