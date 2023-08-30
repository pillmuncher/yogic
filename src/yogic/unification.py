# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A unification mechanism where variables get bound to values.'''


from collections import ChainMap
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import count
from typing import ClassVar, Tuple, Any

from .backtracking import Solutions, Mf, unit, fail, seq, amb, run


@dataclass(frozen=True, slots=True)
class Variable:
    '''Variable objects are bound to values in a monadic computation.'''
    id: int
    counter:ClassVar = count()

def var():
    '''Helper function to create Variables.'''
    return Variable(next(Variable.counter))


class Subst(ChainMap):
    '''A substitution environment that maps Variables to values. This is called
    a variable binding. Variables are bound during monadic computations and
    unbound again during backtracking.'''

    def deref(self, obj):
        '''Chase down Variable bindings.'''
        while isinstance(obj, Variable) and obj in self:
            obj = self[obj]
        return obj

    def smooth(self, obj):
        '''Recursively replace all variables with their bindings.'''
        match self.deref(obj):
            case list() | tuple() as sequence:
                return type(sequence)(self.smooth(each) for each in sequence)
            case thing:
                return thing

    @property
    class proxy(Mapping):
        '''A proxy interface to Subst.'''
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, variable:Variable):
            return self._subst.smooth(variable)
        def __iter__(self):
            return iter(self._subst)
        def __len__(self):
            return len(self._subst)


def compatible(this, that):
    '''Only sequences of same type and length are compatible in unification.'''
    # pylint: disable=C0123
    return type(this) == type(that) and len(this) == len(that)


def _unify(this, that):
    match this, that:
        case _ if this == that:
            # Equal things are already unified:
            return unit
        case list() | tuple(), list() | tuple() if compatible(this, that):
            # Two lists or tuples are unified only if their elements are also:
            # pylint: disable=E1101
            return seq.from_iterable(map(unify, this, that))  # type: ignore
        case Variable(), _:
            # Bind a Variable to another thing:
            return lambda subst: unit(subst.new_child({this: that}))
        case _, Variable():
            # Same as above, but with swapped arguments:
            return lambda subst: unit(subst.new_child({that: this}))
        case _:
            # Unification failed:
            return fail


# Public interface to _unify:
def unify(*pairs:Tuple[Any, Any]) -> Mf:
    '''Unify 'this' and 'that'.
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    # pylint: disable=E1102,W0108
    return lambda subst: seq.from_iterable(  # type: ignore
        _unify(subst.deref(this), subst.deref(that)) for this, that in pairs
    )(subst)


def unify_any(v:Variable, *values) -> Mf:
    return amb.from_iterable(unify((v, value)) for value in values)  # type: ignore

def resolve(goal:Mf) -> Solutions:
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    return (subst.proxy for subst in run(goal, Subst()))
