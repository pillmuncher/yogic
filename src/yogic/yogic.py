# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.19a'
__date__ = '2021-04-15'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'predicate',
    'resolve',
    'unify',
    'var',
)

from collections import namedtuple, ChainMap
from itertools import count
from functools import wraps

from .utils import multimethod
from .backtracking import unit, zero, run, alt, seq


# Variable objects to be bound to values in a monadic computation:
Variable = namedtuple('Variable', 'id')
Variable._counter = count()


def var():
    'Helper function to create Variables:'
    return Variable(next(Variable._counter))


# An environment mapping Variables to the values they are bound to during a
# monadic computation:
class Subst(ChainMap):

    @multimethod
    def chase(self, var: Variable):
        if var in self:
            return self.chase(self[var])
        else:
            return var

    @multimethod
    def chase(self, sequence: (list, tuple)):
        return type(sequence)(self.chase(each) for each in sequence)

    @multimethod
    def chase(self, obj: object):
        return obj

    @property
    class proxy:
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return self._subst.chase(var)


# A polymorphic function that attempts to unify two objects in a Subst():
#
# Bind a Variable to a non-Variable:
@multimethod
def _unify(this: Variable, that: object):
    if this is that:
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
        return seq(*map(unify, this, that))
    else:
        return zero

# Unify other objects only if they're equal:
@multimethod
def _unify(this: object, that: object):
    if this == that:
        return unit
    else:
        return zero


# Public interface to _unify:
def unify(this, that):
    '''Unify "this" and "that".
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    return lambda subst: _unify(subst.chase(this), subst.chase(that))(subst)


def predicate(genfunc):
    'Helper decorator for generator functions.'
    @wraps(genfunc)
    def _(*args, **kwargs):
        return alt(*genfunc(*args, **kwargs))
    return _


def resolve(goal):
    'Start the logical resolution of "goal". Return all solutions.'
    return (subst.proxy for subst in run(goal(Subst())))
