# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.2.2'
__date__ = '2021-04-22'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # re-export from backtracking.py
    'alt',
    'bind',
    'no',
    'run',
    'seq',
    'staralt',
    'starseq',
    'unit',
    'zero',
    # re-export from yogic.py
    'predicate',
    'resolve',
    'unify',
    'var',
)

from .backtracking import alt, bind, no, run, seq, staralt, starseq, unit, zero
from .yogic import predicate, resolve, unify, var

from . import _version
__version__ = _version.get_versions()['version']
