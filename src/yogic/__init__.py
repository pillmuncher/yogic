#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (c) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.18a'
__date__ = '2020-04-13'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # re-export from backtracking.py
    'bind',
    'unit',
    'fail',
    'seq',
    'alt',
    'no',
    'run',
    'recursive',
    # re-export from yogic.py
    'predicate',
    'resolve',
    'unify',
    'var',
)

from .backtracking import bind, unit, fail, seq, alt, no, run, recursive
from .yogic import predicate, resolve, unify, var
