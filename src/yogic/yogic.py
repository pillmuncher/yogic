# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__all__ = (
    'predicate',
    'resolve',
    'unify',
    'var',
)

from collections.abc import Mapping
from collections import namedtuple, ChainMap
from functools import wraps
from itertools import count

from .backtracking import unit, zero, run, seq


# Variable objects to be bound to values in a monadic computation:
Variable = namedtuple('Variable', 'id')
Variable._counter = count()


def var():
    'Helper function to create Variables:'
    return Variable(next(Variable._counter))


class Subst(ChainMap):
    """An environment that maps Variables to the values they are bound to during
    a monadic computation:"""

    def chase(self, obj):
        "Chase down Variable bindings."
        match obj:
            case Variable() as var:
                if var in self:
                    return self.chase(self[var])
                else:
                    return var
            case list() | tuple() as sequence:
                return type(sequence)(self.chase(each) for each in sequence)
            case _:
                return obj

    @property
    class proxy(Mapping):
        "A proxy interface to Subst."
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return self._subst.chase(var)
        def __iter__(self):
            return iter(self._subst)
        def __len__(self):
            return len(self._subst)


def _unify(this: Variable, that: object):
    # Unify two objects in a Subst:
    match this, that:
        case Variable(), object():
            # Bind a Variable to another object:
            if this is that:
                # a Variable, already bound or not, is always bound to itself:
                return unit
            else:
                # bind this to that while creating a new choice point:
                return lambda subst: unit(subst.new_child({this: that}))
        case object(), Variable():
            # Same as above, but with swapped arguments:
            return _unify(that, this)
        case list() | tuple(), list() | tuple():
            # Recursively unify two lists or tuples:
            if type(this) == type(that) and len(this) == len(that):
                return seq.from_iterable(map(unify, this, that))
            else:
                return zero
        case _:
            # Unify other objects only if they're equal:
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


def predicate(func):
    'Helper decorator for yogic functions.'
    @wraps(func)
    def _(*args, **kwargs):
        return lambda v: func(*args, **kwargs)(v)
    return _


def resolve(goal):
    'Start the logical resolution of "goal". Return all solutions.'
    return (subst.proxy for subst in run(goal(Subst())))
