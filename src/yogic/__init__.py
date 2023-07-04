# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A logic programming library.'''

__date__ = '2023-06-26'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # re-export from backtracking.py
    'bind',
    'unit',
    'zero',
    'no',
    'then',
    'alt',
    'seq',
    # re-export from unification.py
    'predicate',
    'resolve',
    'unify',
    'var',
)

from .backtracking import bind, unit, zero, no, then, seq, alt, predicate
from .unification import resolve, unify, var

from . import _version
__version__ = _version.get_versions()['version']
