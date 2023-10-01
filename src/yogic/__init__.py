# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A simple combinator library for logic programming.'''


# It uses the Triple-Barreled Continuation Monad for resolution,
# backtracking, and branch pruning.
#
#
# “The continuation that obeys only obvious stack semantics,
# O grasshopper, is not the true continuation.” — Guy Steele.
#
#
# To keep more closely to the terminology of logic programming and to not
# bother users too much with the terminology of monads and continuations, the
# monadic computation type is called 'Step' and the monadic continuation type
# is called 'Goal'.
#
# A set of basic combinators you would expect in such a library is provided,
# like 'unit' (succeeds once), 'fail' (never succeeds), and 'cut' (succeeds
# once, then curtails backtracking at the previous choice point), 'and' for
# conjunction of goals, 'or' for adjunction, 'not' for negation, and 'unify'
# and 'unify_any' for unification. The resolution process is started by
# calling 'resolve' on a goal and then iterating over the solutions, which
# consist of substitution environments (proxy mappings) of variables to their
# bindings.
#
# The code makes use of the algebraic structure of the monadic combinators:
# 'unit' and 'then' form a Monoid over monadic combinator functions, as do
# 'fail' and 'choice', which allows us to fold a sequence of combinators into
# a single one. Taken thogether, these structures form a Distributive Lattice
# with 'then' as the meet (infimum) and 'choice' as the join (supremum)
# operator, a fact that is not utilized in the code, though. Because of the
# sequential nature of the employed resolution algorithm combined with the
# 'cut', neither the lattice nor the monoids are commutative.
#
# Due to the absence of Tail Call Elimination in C#, Trampolining with
# Thunking is used to prevent stack overflows.


__date__ = '2023-07-04'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'
__version__ = "0.7.2"

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


Result = Optional[tuple[Subst, 'Next']]
Next = Callable[[], Result]
Emit = Callable[[Subst, Next], Result]
Step = Callable[[Emit, Next, Next], Result]
Goal = Callable[[Subst], Step]


def tailcall(goal:Step|Emit|Next) -> Callable[..., Result]:
    '''Tail-call elimination.'''
    @wraps(goal)  # type: ignore
    def wrapped(*args) -> Result:
        return (), wraps(goal)(lambda: goal(*args))  # type: ignore
    return wrapped


@tailcall
def success(subst:Subst, backtrack:Next) -> Result:
    '''Return the Subst subst and start searching for more Solutions.'''
    return subst, backtrack


@tailcall
def failure() -> Result:
    '''Fail.'''


def bind(step:Step, goal:Goal) -> Step:
    '''Return the result of applying goal to step.'''
    @tailcall
    def mb(succeed:Emit, backtrack:Next, escape:Next) -> Result:
        @tailcall
        def on_success(subst:Subst, backtrack:Next) -> Result:
            return goal(subst)(succeed, backtrack, escape)
        return step(on_success, backtrack, escape)
    return mb


def unit(subst:Subst) -> Step:
    '''Take the single value subst into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    @tailcall
    def step(succeed:Emit, backtrack:Next, escape:Next) -> Result:
        return succeed(subst, backtrack)
    return step


def cut(subst:Subst) -> Step:
    '''Succeed, then prune the search tree at the previous choice point.'''
    @tailcall
    def step(succeed:Emit, backtrack:Next, escape:Next) -> Result:
        # we commit to the current execution path by injecting
        # the escape continuation as our new backtracking path:
        return succeed(subst, escape)
    return step


def fail(subst:Subst) -> Step:
    '''Ignore the argument and start backtracking. Represents failure.
    Together with 'coice', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.
    It is also mzero.'''
    @tailcall
    def step(succeed:Emit, backtrack:Next, escape:Next) -> Result:
        return backtrack()
    return step


def then(goal1:Goal, goal2:Goal) -> Goal:
    '''Apply two monadic functions goal1 and goal2 in sequence.
    Together with 'unit', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def goal(subst:Subst) -> Step:
        return bind(goal1(subst), goal2)
    return goal


def seq(*goals:Goal) -> Goal:
    '''Find solutions for all goals in sequence.'''
    # pylint: disable=E1101
    return seq.from_iterable(goals)  # type: ignore


@extend(seq)
def from_iterable(goals:Iterable[Goal]) -> Goal:  # type: ignore
    '''Find solutions for all goals in sequence.'''
    return reduce(then, goals, unit)  # type: ignore
del from_iterable


def choice(goal1:Goal, goal2:Goal) -> Goal:
    '''Succeeds if either of the goal functions succeeds.
    Together with 'fail', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.'''
    def goal(subst:Subst) -> Step:
        @tailcall
        def step(succeed:Emit, backtrack:Next, escape:Next) -> Result:
            # we pass goal and goal2 the same success continuation, so we
            # can invoke goal and goal2 at the same point in the computation:
            @tailcall
            def on_failure() -> Result:
                return goal2(subst)(succeed, backtrack, escape)
            return goal1(subst)(succeed, on_failure, escape)
        return step
    return goal


def amb(*goals:Goal) -> Goal:
    '''Find solutions for some goals. This creates a choice point.'''
     # pylint: disable=E1101
    return amb.from_iterable(goals)  # type: ignore


# pylint: disable=E0102
@extend(amb)  # type: ignore
def from_iterable(goals:Iterable[Goal]) -> Goal:
    '''Find solutsons for some goals. This creates a choice point.'''
    joined = reduce(choice, goals, fail)  # type: ignore
    def goal(subst:Subst) -> Step:
        @tailcall
        def step(succeed:Emit, backtrack:Next, escape:Next) -> Result:
            # we serialize the goals and inject the
            # fail continuation as the escape path:
            return joined(subst)(succeed, backtrack, backtrack)
        return step
    return goal
del from_iterable


def no(goal:Goal) -> Goal:
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    return amb(seq(goal, cut, fail), unit)


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
def unify(*pairs:tuple[Any, Any]) -> Goal:
    '''Unify 'this' and 'that'.
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    # pylint: disable=E1101,W0108
    return lambda subst: seq.from_iterable(  # type: ignore
        _unify(subst.deref(this), subst.deref(that)) for this, that in pairs
    )(subst)


def unify_any(var:Variable, *values) -> Goal:
    ''' Tries to unify a variable with any one of objects.
    Fails if no object is unifiable.'''
     # pylint: disable=E1101
    return amb.from_iterable(unify((var, value)) for value in values)  # type: ignore


def predicate(func:Callable[..., Goal]) -> Callable[..., Goal]:
    '''Helper decorator for backtrackable functions.'''
    # All this does is to create another level of indirection.
    @wraps(func)
    def pred(*args, **kwargs) -> Goal:
        def goal(subst:Subst) -> Step:
            return func(*args, **kwargs)(subst)
        return goal
    return pred


def resolve(goal:Goal) -> Iterable[Mapping]:
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    result: Result = goal(Subst())(success, failure, failure)
    while result:
        subst, next = result  # type: ignore
        if subst:
            yield subst.proxy  # type: ignore
        result = next()
