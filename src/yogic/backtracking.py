# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A monad for backtracking. Hence it's called the Backtracking Monad.
Actually, it's just a triple-barrelled Continuation Monad grafted onto 
the List Monad.'''


# “The continuation that obeys only obvious stack semantics,
# O grasshopper, is not the true continuation.” — Guy Steele.


from collections.abc import Iterable
from functools import wraps, reduce
from itertools import islice
from typing import Callable, TypeVar


Value = TypeVar('Value')
Solution = TypeVar('Solution')

Solutions = Iterable[Solution]
Escape = Callable[[], Solutions]
Failure = Callable[[], Solutions]
Success = Callable[[Value], Solutions]
Ma = Callable[[Success, Failure, Escape], Solutions]
Mf = Callable[[Value], Ma]


# the function failure() is always called with no arguments and
# always returns an 'empty' iterable. we can just use tuple():
failure = tuple


def bind(ma:Ma, mf:Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        def _success(v:Value) -> Solutions:
            # we inject new fail and escape continuations, so
            # that the received ones don't get called twice:
            yield from mf(v)(y, failure, failure)
        yield from ma(_success, n, e)
    return _ma


def unit(v:Value) -> Ma:
    '''Take the single value v into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        # after we return all solutions from the success continuation,
        # we invoke the fail continuation n() to kick off backtracking:
        yield from y(v)
        yield from n()
    return _ma


def fail(_:Value) -> Ma:
    '''Ignore the argument and return an 'empty' monad. Represents failure.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        yield from n()
    return _ma


def cut(v:Value) -> Ma:
    '''Commit to the first solution, thus pruning the 
    search tree at the previous choice point.'''
    def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
        # we commit to the first solution (if it exists) and invoke 
        # the escape continuation as the backtracking path:
        yield from islice(y(v), 1)
        yield from e()
    return _ma


def then(mf:Mf, mg:Mf) -> Mf:
    '''Apply two monadic functions mf and mg in sequence.
    Together with 'unit', this makes the monad also a monoid.'''
    def _mf(v:Value) -> Ma:
        return bind(mf(v), mg)
    return _mf


def _seq_from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions matching all mfs.'''
    return reduce(then, mfs, unit)  # type: ignore


def seq(*mfs:Mf) -> Mf:
    '''Find solutions matching all mfs.'''
    return _seq_from_iterable(mfs)

seq.from_iterable = _seq_from_iterable  # type: ignore


def choice(mf:Mf, mg:Mf) -> Mf:
    '''Succeeds if either of the Mf functions succeeds.'''
    def _mf(v:Value) -> Ma:
        def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
            # we close over the current environment, so we can invoke
            # mf and mg at the same point in the computation:
            def _failure() -> Solutions:
                yield from mg(v)(y, n, e)
            yield from mf(v)(y, _failure, e)
        return _ma
    return _mf


def _amb_from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions matching any one of mfs.'''
    def _mf(v:Value) -> Ma:
        def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
            # we serialize the mfs and make the received fail continuation n()
            # our new escape continuation, so we can jump out of a computation:
            yield from reduce(choice, mfs, fail)(v)(y, n, n)  # type: ignore
        return _ma
    return _mf


def amb(*mfs:Mf) -> Mf:
    '''Find solutions matching any one of mfs.'''
    return _amb_from_iterable(mfs)

amb.from_iterable = _amb_from_iterable  # type: ignore


def predicate(p:Callable[..., Mf]) -> Callable[..., Mf]:
    '''Helper decorator for backtrackable functions.'''
    # All this does is to create another level of indirection.
    @wraps(p)
    def _p(*args, **kwargs) -> Mf:
        def _mf(v:Value) -> Ma:
            return p(*args, **kwargs)(v)
        return _mf
    return _p


def no(mf:Mf) -> Mf:
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    def _mf(v:Value) -> Ma:
        def _ma(y:Success, n:Failure, e:Escape) -> Solutions:
            for _ in mf(v)(y, n, e):
                # If at least one solution is found, fail immediately:
                return fail(v)(y, n, e)
            else:  # pylint: disable=W0120
                # If no solution is found, succeed:
                return unit(v)(y, n, e)
        return _ma
    return _mf
