# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A simple combinator library for logic programming.'''

__date__ = '2023-07-04'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # re-export from .backtracking
    'bind',
    'unit',
    'zero',
    'no',
    'then',
    'alt',
    'seq',
    'predicate',
    # re-export from .unification
    'resolve',
    'unify',
    'var',
)

from .backtracking import bind, unit, zero, no, then, seq, alt, predicate
from .unification import resolve, unify, var

from . import _version
__version__ = _version.get_versions()['version']
