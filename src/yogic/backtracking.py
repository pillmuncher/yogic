# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A monad for backtracking. Hence it's called the Backtracking Monad.
Actually, it's just a triple-barrelled Continuation Monad grafted onto
the List Monad.'''


# “The continuation that obeys only obvious stack semantics,
# O grasshopper, is not the true continuation.” — Guy Steele.


from collections.abc import Iterable
from functools import wraps
from typing import Callable, TypeVar

from .extension import extend
from .functional import foldr


Value = TypeVar('Value')
Solution = TypeVar('Solution')

Solutions = Iterable[Solution]
Escape = Callable[[], Solutions]
Failure = Callable[[], Solutions]
Success = Callable[[Value, Failure|Escape], Solutions]
Ma = Callable[[Success, Failure, Escape], Solutions]
Mf = Callable[[Value], Ma]


def success(v:Value, b:Failure|Escape) -> Solutions:
    '''Return the Solution v and start searching for more Solutions.'''
    yield v
    yield from b()


def failure() -> Solutions:
    '''Fail.'''
    yield from ()


def bind(ma:Ma, mf:Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    def mb(y:Success, n:Failure, e:Escape) -> Solutions:
        def on_success(v:Value, b:Failure|Escape) -> Solutions:
            return mf(v)(y, b, e)
        return ma(on_success, n, e)
    return mb


def unit(v:Value) -> Ma:
    '''Take the single value v into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def ma(y:Success, n:Failure, e:Escape) -> Solutions:
        return y(v, n)
    return ma


def cut(v:Value) -> Ma:
    '''Succeed, then prune the search tree at the previous choice point.'''
    def ma(y:Success, n:Failure, e:Escape) -> Solutions:
        # we commit to the current execution path by injecting
        # the escape continuation as our new backtracking path:
        return y(v, e)
    return ma


def fail(v:Value) -> Ma:
    '''Ignore the argument and start backtracking. Represents failure.
    Together with 'coice', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.
    It is also mzero.'''
    def ma(y:Success, n:Failure, e:Escape) -> Solutions:
        return n()
    return ma


def then(mf:Mf, mg:Mf) -> Mf:
    '''Apply two monadic functions mf and mg in sequence.
    Together with 'unit', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def mgf(v:Value) -> Ma:
        return bind(mf(v), mg)
    return mgf


def seq(*mfs:Mf) -> Mf:
    '''Find solutions for all mfs in sequence.'''
     # pylint: disable=E1101
    return seq.from_iterable(mfs) # type: ignore


@extend(seq)
def from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions for all mfs in sequence.'''
    return foldr(then, mfs, unit)
del from_iterable


def choice(mf:Mf, mg:Mf) -> Mf:
    '''Succeeds if either of the Mf functions succeeds.
    Together with 'fail', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.'''
    def mgf(v:Value) -> Ma:
        def ma(y:Success, n:Failure, e:Escape) -> Solutions:
            # we pass mf and mg the same success continuation, so we
            # can invoke mf and mg at the same point in the computation:
            def on_failure() -> Solutions:
                return mg(v)(y, n, e)
            return mf(v)(y, on_failure, e)
        return ma
    return mgf


def amb(*mfs:Mf) -> Mf:
    '''Find solutions for some mfs. This creates a choice point.'''
     # pylint: disable=E1101
    return amb.from_iterable(mfs) # type: ignore


# pylint: disable=E0102
@extend(amb) # type: ignore
def from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutsons for some mfs. This creates a choice point.'''
    joined = foldr(choice, mfs, fail)
    def mf(v:Value) -> Ma:
        def ma(y:Success, n:Failure, e:Escape) -> Solutions:
            # we serialize the mfs and inject the
            # fail continuation as the escape path:
            return joined(v)(y, n, n)
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
        def mf(v:Value) -> Ma:
            return p(*args, **kwargs)(v)
        return mf
    return pred


def run(mf:Mf, v:Value) -> Solutions:
    '''Start the monadic computation represented by mf.'''
    return mf(v)(success, failure, failure)
