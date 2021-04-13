#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (c) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.18a'
__date__ = '2020-04-13'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    # export from here
    'predicate',
    'resolve',
    'unify',
    'var',
    # re-export from lib.backtracking
    'bind',
    'unit',
    'fail',
    'seq',
    'alt',
    'no',
    'run',
    'recursive',
)

from collections import namedtuple, ChainMap
from itertools import count
from functools import wraps

from . import multimethod
from .backtracking import bind, unit, fail, seq, alt, no, run, recursive
from .backtracking import alt_unstarred, seq_unstarred


# Variable objects to be bound to values in a monadic computation:
Variable = namedtuple('Variable', 'id')
Variable._counter = count()

def var():
    'Helper function to create Variables:'
    return Variable(next(Variable._counter))


# An environment mapping Variables to the values they are bound to during a
# monadic computation:
class Subst(ChainMap):
    @property
    class proxy:
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return chase(var, self._subst)


def resolve(goal):
    'Start the logical resolution of "goal". Return all solutions.'
    return (subst.proxy for subst in run(goal(Subst())))


# A polymorphic function that chases "pointers" to bindings in an environment.
@multimethod
def chase(var: Variable, subst: Subst):
    if var in subst:
        return chase(subst[var], subst)
    else:
        return var

@multimethod
def chase(seq: (list, tuple), subst: Subst):
    return type(seq)(chase(each, subst) for each in seq)

@multimethod
def chase(obj: object, subst: Subst):
    return obj


# A polymorphic function that attempts to unify two objects in a Subst():
#
# Bind Variables to values:
@multimethod
def _unify(this: Variable, that: object):
    if this == that:
        # a Variable, already bound or not, is always bound to itself:
        return unit
    else:
        # bind this to that while creating a new choice point:
        return lambda subst: unit(subst.new_child({this: that}))

# Same as above, but with swapped arguments:
@multimethod
def _unify(this: object, that: Variable):
    return _unify(that, this)

# Recursively unify two lists or tuples:
@multimethod
def _unify(this: (list, tuple), that: (list, tuple)):
    if type(this) == type(that) and len(this) == len(that):
        return seq_unstarred(map(unify, this, that))
    else:
        return fail

# Unify other objects only if they're equal:
@multimethod
def _unify(this: object, that: object):
    if this == that:
        return unit
    else:
        return fail


# Public interface to _unify:
def unify(this, that):
    '''Unify "this" and "that".
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    return lambda subst: _unify(chase(this, subst), chase(that, subst))(subst)


def predicate(genfunc):
    'Helper decorator for generator functions.'
    @wraps(genfunc)
    def _(*args, **kwargs):
        return alt_unstarred(genfunc(*args, **kwargs))
    return _
