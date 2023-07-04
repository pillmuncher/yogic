# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>




from collections import ChainMap
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import count
from typing import ClassVar

from .backtracking import Solutions, Mf, unit, zero, seq


@dataclass(frozen=True, slots=True)
class Variable:
    '''Variable objects are bound to values in a monadic computation.'''
    id: int  # pylint: disable=C0103
    counter:ClassVar = count()


def var():
    '''Helper function to create Variables.'''
    return Variable(next(Variable.counter))


class Subst(ChainMap):
    '''An environment that maps Variables to values. This is called a variable
    binding. Variables are bound during monadic computations and unbound again
    during backtracking.'''

    def chase(self, obj):
        '''Chase down Variable bindings.'''
        while isinstance(obj, Variable) and obj in self:
            obj = self[obj]
        match obj:
            case Variable() as variable:
                return variable
            case list() | tuple() as sequence:
                return type(sequence)(self.chase(each) for each in sequence)
            case _:
                return obj

    @property
    class proxy(Mapping):  # pylint: disable=C0103
        '''A proxy interface to Subst.'''
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, variable:Variable):
            return self._subst.chase(variable)
        def __iter__(self):
            return iter(self._subst)
        def __len__(self):
            return len(self._subst)


def compatible(this, that):
    '''Only sequences of same type and length are compatible in unification.'''
    # pylint: disable=C0123
    return type(this) == type(that) and len(this) == len(that)


def _unify(this, that) -> Mf:  # type: ignore
    match this, that:
        case _ if this == that:
            # Unify objects if they're equal:
            return unit
        case Variable(), _:
            # bind this to that while creating a new choice point:
            return lambda subst: unit(subst.new_child({this: that}))
        case _, Variable():
            # Same as above, but with swapped arguments:
            return lambda subst: unit(subst.new_child({that: this}))
        case list() | tuple(), list() | tuple() if compatible(this, that):
            # Recursively unify two lists or tuples:
            return seq.from_iterable(map(unify, this, that))  # type: ignore
        case _:
            # Unification failed:
            return zero


# Public interface to _unify:
def unify(this, that) -> Mf:
    '''Unify 'this' and 'that'.
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    # pylint: disable=E1102,W0108
    return lambda subst: _unify(subst.chase(this), subst.chase(that))(subst)


def yield_proxy(subst):
    '''Yield a proxy of the subst once.'''
    yield subst.proxy


def resolve(goal:Mf) -> Solutions:
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    return goal(Subst())(yield_proxy)
