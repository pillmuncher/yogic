from __future__ import annotations
# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A simple combinator library for logic programming.'''


# “The continuation that obeys only obvious stack semantics,
# O grasshopper, is not the true continuation.” — Guy Steele.


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

from . import _version
__version__ = _version.get_versions()['version']

from collections import ChainMap
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import count
from functools import reduce, wraps
from typing import Any, Callable, ClassVar, Tuple, TypeVar

from .extension import extend


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


Failure = Callable[[], Iterable[Subst]]
Success = Callable[[Subst, Failure], Iterable[Subst]]
Ma = Callable[[Success, Failure, Failure], Iterable[Subst]]
Mf = Callable[[Subst], Ma]


def trampoline(function, *args):
    '''Tail-call elimination driver.'''
    while bounce := function(*args):
        result, function, *args = bounce
        if result:
            yield result


def tailcall(function):
    '''Tail-call elimination decorator.'''
    @wraps(function)
    def launch(*args):
        return None, function, *args
    return launch


@tailcall
def success(s:Subst, b:Failure) -> Tuple[Subst, Failure]:
    '''Return the Subst s and start searching for more Iterable[Subst].'''
    return s, b


@tailcall
def failure() -> None:
    '''Fail.'''


def bind(ma:Ma, mf:Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    def mb(y:Success, n:Failure, e:Failure) -> Iterable[Subst]:
        @tailcall
        def on_success(s:Subst, b:Failure) -> Iterable[Subst]:
            return mf(s)(y, b, e)
        return ma(on_success, n, e)
    return mb


def unit(s:Subst) -> Ma:
    '''Take the single value s into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def ma(y:Success, n:Failure, e:Failure) -> Iterable[Subst]:
       return y(s, n)
    return ma


def cut(s:Subst) -> Ma:
    '''Succeed, then prune the search tree at the previous choice point.'''
    def ma(y:Success, n:Failure, e:Failure) -> Iterable[Subst]:
        # we commit to the current execution path by injecting
        # the escape continuation as our new backtracking path:
        return y(s, e)
    return ma


def fail(s:Subst) -> Ma:
    '''Ignore the argument and start backtracking. Represents failure.
    Together with 'coice', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.
    It is also mzero.'''
    def ma(y:Success, n:Failure, e:Failure) -> Iterable[Subst]:
        return n()
    return ma


def then(mf:Mf, mg:Mf) -> Mf:
    '''Apply two monadic functions mf and mg in sequence.
    Together with 'unit', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def mgf(s:Subst) -> Ma:
        return bind(mf(s), mg)
    return mgf


def seq(*mfs:Mf) -> Mf:
    '''Find solutions for all mfs in sequence.'''
     # pylint: disable=E1101
    return seq.from_iterable(mfs)


@extend(seq)
def from_iterable(mfs:Iterable[Mf]) -> Mf: # type: ignore
    '''Find solutions for all mfs in sequence.'''
    return reduce(then, mfs, unit)
del from_iterable


def choice(mf:Mf, mg:Mf) -> Mf:
    '''Succeeds if either of the Mf functions succeeds.
    Together with 'fail', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.'''
    def mgf(s:Subst) -> Ma:
        def ma(y:Success, n:Failure, e:Failure) -> Iterable[Subst]:
            # we pass mf and mg the same success continuation, so we
            # can invoke mf and mg at the same point in the computation:
            @tailcall
            def on_failure() -> Iterable[Subst]:
                return mg(s)(y, n, e)
            return mf(s)(y, on_failure, e)
        return ma
    return mgf


def amb(*mfs:Mf) -> Mf:
    '''Find solutions for some mfs. This creates a choice point.'''
     # pylint: disable=E1101
    return amb.from_iterable(mfs)


# pylint: disable=E0102
@extend(amb)
def from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutsons for some mfs. This creates a choice point.'''
    joined = reduce(choice, mfs, fail)
    def mf(s:Subst) -> Ma:
        def ma(y:Success, n:Failure, e:Failure) -> Iterable[Subst]:
            # we serialize the mfs and inject the
            # fail continuation as the escape path:
            return joined(s)(y, n, n)
        return ma
    return mf
del from_iterable


def no(mf:Mf) -> Mf:
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    return amb(seq(mf, cut, fail), unit)


def predicate(p:Callable[..., Mf]) -> Callable[..., Mf]:
    '''Helper decorator for backtrackable functions.'''
    # All this does is to create another level of indirection.
    @wraps(p)
    def pred(*args, **kwargs) -> Mf:
        def mf(s:Subst) -> Ma:
            return p(*args, **kwargs)(s)
        return mf
    return pred


def run(mf:Mf, s:Subst) -> Iterable[Subst]:
    '''Start the monadic computation represented by mf.'''
    return trampoline(mf(s), success, failure, failure)



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

def resolve(goal:Mf) -> Iterable[Subst]:
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    return (subst.proxy for subst in run(goal, Subst()))
