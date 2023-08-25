# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A simple combinator library for logic programming.'''

__date__ = '2023-07-04'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # re-export from .backtracking
    'bind',
    'unit',
    'fail',
    'no',
    'then',
    'amb',
    'seq',
    'predicate',
    'cut',
    # re-export from .unification
    'resolve',
    'unify',
    'unify_any',
    'var',
)

from .backtracking import bind, unit, fail, no, then, seq, amb, predicate, cut
from .unification import resolve, unify, unify_any, var

from . import _version
__version__ = _version.get_versions()['version']
