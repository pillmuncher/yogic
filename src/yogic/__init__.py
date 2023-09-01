# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A simple combinator library for logic programming.'''


# “The continuation that obeys only obvious stack semantics,
# O grasshopper, is not the true continuation.” — Guy Steele.

from __future__ import annotations

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

from collections import ChainMap
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import reduce, wraps
from itertools import count
from typing import Any, Callable, ClassVar, Optional

from .extension import extend

from . import _version
__version__ = _version.get_versions()['version']


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


Solutions = Iterable[Subst]
ThunkData = Optional[tuple[Solutions, 'Failure']]
Failure = Callable[[], ThunkData]
Success = Callable[[Subst, Failure], ThunkData]
Ma = Callable[[Success, Failure, Failure], ThunkData]
Mf = Callable[[Subst], Ma]
Cont = Ma | Success | Failure


def tailcall(cont) -> Callable[..., ThunkData]:
    '''Tail-call elimination.'''
    @wraps(cont)
    def wrapped(*args) -> ThunkData:
        return (), wraps(cont)(lambda: cont(*args))
    return wrapped


@tailcall
def success(s:Subst, b:Failure) -> ThunkData:
    '''Return the Subst s and start searching for more Result.'''
    return [s], b


@tailcall
def failure() -> ThunkData:
    '''Fail.'''


def bind(ma:Ma, mf:Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    @tailcall
    def mb(y:Success, n:Failure, e:Failure) -> ThunkData:
        @tailcall
        def on_success(s:Subst, b:Failure) -> ThunkData:
            return mf(s)(y, b, e)
        return ma(on_success, n, e)
    return mb


def unit(s:Subst) -> Ma:
    '''Take the single value s into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    @tailcall
    def ma(y:Success, n:Failure, e:Failure) -> ThunkData:
        return y(s, n)
    return ma


def cut(s:Subst) -> Ma:
    '''Succeed, then prune the search tree at the previous choice point.'''
    @tailcall
    def ma(y:Success, n:Failure, e:Failure) -> ThunkData:
        # we commit to the current execution path by injecting
        # the escape continuation as our new backtracking path:
        return y(s, e)
    return ma


def fail(s:Subst) -> Ma:
    '''Ignore the argument and start backtracking. Represents failure.
    Together with 'coice', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.
    It is also mzero.'''
    @tailcall
    def ma(y:Success, n:Failure, e:Failure) -> ThunkData:
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
    return seq.from_iterable(mfs)  # type: ignore


@extend(seq)
def from_iterable(mfs:Iterable[Mf]) -> Mf:  # type: ignore
    '''Find solutions for all mfs in sequence.'''
    return reduce(then, mfs, unit)  # type: ignore
del from_iterable


def choice(mf:Mf, mg:Mf) -> Mf:
    '''Succeeds if either of the Mf functions succeeds.
    Together with 'fail', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.'''
    def mgf(s:Subst) -> Ma:
        @tailcall
        def ma(y:Success, n:Failure, e:Failure) -> ThunkData:
            # we pass mf and mg the same success continuation, so we
            # can invoke mf and mg at the same point in the computation:
            @tailcall
            def on_failure() -> ThunkData:
                return mg(s)(y, n, e)
            return mf(s)(y, on_failure, e)
        return ma
    return mgf


def amb(*mfs:Mf) -> Mf:
    '''Find solutions for some mfs. This creates a choice point.'''
     # pylint: disable=E1101
    return amb.from_iterable(mfs)  # type: ignore


# pylint: disable=E0102
@extend(amb)  # type: ignore
def from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutsons for some mfs. This creates a choice point.'''
    joined = reduce(choice, mfs, fail)  # type: ignore
    def mf(s:Subst) -> Ma:
        @tailcall
        def ma(y:Success, n:Failure, e:Failure) -> ThunkData:
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
            return seq.from_iterable(map(unify, this, that))
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
def unify(*pairs:tuple[Any, Any]) -> Mf:
    '''Unify 'this' and 'that'.
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    # pylint: disable=E1101,W0108
    return lambda subst: seq.from_iterable(  # type: ignore
        _unify(subst.deref(this), subst.deref(that)) for this, that in pairs
    )(subst)


def unify_any(v:Variable, *values) -> Mf:
    ''' Tries to unify a variable with any one of objects.
    Fails if no object is unifiable.'''
     # pylint: disable=E1101
    return amb.from_iterable(unify((v, value)) for value in values)  # type: ignore


def resolve(goal:Mf) -> Iterable[Mapping]:
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    thunk:Failure = lambda: goal(Subst())(success, failure, failure)
    while thunk_data := thunk():
        solutions, thunk = thunk_data  # type: ignore
        print('>>>', thunk.__name__)
        for subst in solutions:  # type: ignore
            yield subst.proxy  # type: ignore
