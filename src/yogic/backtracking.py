# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A monad for backtracking. Hence it's called the Backtracking Monad.
Actually, it's just a triple-barrelled Continuation Monad grafted onto
the List Monad.'''


# “The continuation that obeys only obvious stack semantics,
# O grasshopper, is not the true continuation.” — Guy Steele.


from collections.abc import Iterable
from functools import wraps, reduce
from typing import Callable, TypeVar


Value = TypeVar('Value')
Solution = TypeVar('Solution')

Solutions = Iterable[Solution]
Escape = Callable[[], Solutions]
Failure = Callable[[], Solutions]
Success = Callable[[Value, Failure, Escape], Solutions]
Ma = Callable[[Success, Failure, Escape], Solutions]
Mf = Callable[[Value], Ma]


def success(v:Value, n:Failure, e:Escape) -> Solutions:
    '''Return the Solution v and start searching for more Solutions.'''
    # after we return the solution we invoke the
    # fail continuation to kick off backtracking:
    yield v
    yield from n()


def failure() -> Solutions:
    '''Fail and start searching for Solutions.'''
    return ()


def bind(ma:Ma, mf:Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        def _success(v:Value, m:Failure, _:Escape) -> Solutions:
            return mf(v)(y, m, e)
        return ma(_success, n, e)
    return _ma


def unit(v:Value) -> Ma:
    '''Take the single value v into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        return y(v, n, e)
    return _ma


def fail(v:Value) -> Ma:
    '''Ignore the argument and return an 'empty' monad. Represents failure.
    Together with 'coice', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        return n()
    return _ma


def then(mf:Mf, mg:Mf) -> Mf:
    '''Apply two monadic functions mf and mg in sequence.
    Together with 'unit', this makes the monad also a monoid. Together
    with 'fail' and 'choice', this makes the monad also a lattice.'''
    def _mf(v:Value) -> Ma:
        return bind(mf(v), mg)
    return _mf


def _seq_from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions for all mfs'''
    return reduce(then, mfs, unit)  # type: ignore


def seq(*mfs:Mf) -> Mf:
    '''Find solutions for all mfs'''
    return _seq_from_iterable(mfs)

seq.from_iterable = _seq_from_iterable  # type: ignore


def choice(mf:Mf, mg:Mf) -> Mf:
    '''Succeeds if either of the Mf functions succeeds.
    Together with 'fail', this makes the monad also a monoid. Together
    with 'unit' and 'then', this makes the monad also a lattice.'''
    def _mf(v:Value) -> Ma:
        def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
            # we close over the current environment, so we can invoke
            # mf and mg at the same point in the computation:
            def _failure() -> Solutions:
                return mg(v)(y, n, e)
            return mf(v)(y, _failure, e)
        return _ma
    return _mf


def cut(v:Value) -> Ma:
    '''Prune the search tree at the previous choice point.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        # we commit to the first solution (if it exists) by invoking
        # the escape continuation and making it our backtracking path:
        yield from y(v, e, e)
    return _ma


def _amb_from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions for some mfs. This creates a choice point.'''
    def _mf(v:Value) -> Ma:
        def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
            # we serialize the mfs and make the received fail continuation n()
            # our new escape continuation, so we can jump out of a computation:
            return reduce(choice, mfs, fail)(v)(y, n, n)  # type: ignore
        return _ma
    return _mf


def amb(*mfs:Mf) -> Mf:
    '''Find solutions for some mfs. This creates a choice point.'''
    return _amb_from_iterable(mfs)

amb.from_iterable = _amb_from_iterable  # type: ignore


def no(mf:Mf) -> Mf:
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    return amb(seq(mf, cut, fail), unit)


def predicate(p:Callable[..., Mf]) -> Callable[..., Mf]:
    '''Helper decorator for backtrackable functions.'''
    # All this does is to create another level of indirection.
    @wraps(p)
    def _p(*args, **kwargs) -> Mf:
        def _mf(v:Value) -> Ma:
            return p(*args, **kwargs)(v)
        return _mf
    return _p


def run(mf:Mf, v:Value) -> Solutions:
    '''Start the monadic computation represented by mf.'''
    return mf(v)(success, failure, failure)
