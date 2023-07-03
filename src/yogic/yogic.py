# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

from __future__ import annotations

from collections import namedtuple, ChainMap
from collections.abc import Iterator, Mapping, Sequence
from functools import wraps
from itertools import count
from typing import Any, Callable

from .backtracking import Result, Mf, unit, zero, seq, run


# Variable objects to be bound to values in a monadic computation:
Variable = namedtuple('Variable', 'id')
_var_counter = count()


def var() -> Variable:
    '''Helper function to create Variables.'''
    return Variable(next(_var_counter))


class Subst(ChainMap):
    '''An environment that maps Variables to the values they are bound to during
    a monadic computation.'''

    def chase(self, obj:Any):
        '''Chase down Variable bindings.'''
        match obj:
            case Variable() as variable if variable in self:
                return self.chase(self[variable])
            case Variable() as variable:
                return variable
            case list() | tuple() as sequence:
                return type(sequence)(self.chase(each) for each in sequence)
            case _:
                return obj

    @property
    class proxy(Mapping):  # pylint: disable=C0103
        '''A proxy interface to Subst.'''
        def __init__(self, subst:Subst):
            self._subst = subst
        def __getitem__(self, variable:Variable) -> Any:
            return self._subst.chase(variable)
        def __iter__(self) -> Iterator:
            return iter(self._subst)
        def __len__(self) -> int:
            return len(self._subst)


def compatible(this:Sequence, that:Sequence) -> bool:
    '''Only sequences of same type and length are compatible in unification.'''
    return type(this) == type(that) and len(this) == len(that)  # pylint: disable=C0123


def _unify(this:Any, that:Any) -> Mf:
    # Unify two objects in a Subst:
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
    # Unification failed:
    return zero

# Public interface to _unify:
def unify(this:Any, that:Any) -> Mf:
    '''Unify 'this' and 'that'.
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    return lambda subst: _unify(subst.chase(this), subst.chase(that))(subst)  # pylint: disable=E1102,W0108


def predicate(func:Callable[..., Mf]) -> Callable[..., Mf]:
    '''Helper decorator for yogic functions.'''
    @wraps(func)
    def _(*args, **kwargs):
        return lambda subst: func(*args, **kwargs)(subst)  # pylint: disable=W0108
    return _


def resolve(goal:Mf) -> Result:
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    return (subst.proxy for subst in run(goal(Subst())))
