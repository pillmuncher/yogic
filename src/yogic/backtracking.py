# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

'''A monad for backtracking. Hence it's called the Backtracking Monad.
Actually, it's just the Continuation Monad grafted onto the List Monad.'''


from collections.abc import Iterable
from functools import reduce, wraps
from itertools import chain
from typing import Callable, TypeVar


Value = TypeVar('Value')
Solution = TypeVar('Solution')

Solutions = Iterable[Solution]
Cont = Callable[[Value], Solutions]
Ma = Callable[[Cont], Solutions]
Mf = Callable[[Value], Ma]


def bind(ma:Ma, mf:Mf) -> Ma:
    '''Return the result of applying mf to ma.'''
    return lambda c: ma(lambda v: mf(v)(c))


def unit(v:Value) -> Ma:
    '''Take the single value v into the monad. Represents success.
    Together with 'then', this makes the monad also a monoid.'''
    return lambda c: c(v)  # Finally call the continuation.


def zero(_:Value) -> Ma:
    '''Ignore the argument and return an 'empty' value. Represents failure.'''
    return lambda _: ()  # Skip the continuation.


def then(mf:Mf, mg:Mf) -> Mf:
    '''Apply two monadic functions mf and mg in sequence.
    Together with 'unit', this makes the monad also a monoid.'''
    return lambda v: bind(mf(v), mg)


def _seq_from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions matching all mfs.'''
    return reduce(then, mfs, unit)  # type: ignore


def seq(*mfs:Mf) -> Mf:
    '''Find solutions matching all mfs.'''
    return _seq_from_iterable(mfs)

seq.from_iterable = _seq_from_iterable  # type: ignore


def _alt_from_iterable(mfs:Iterable[Mf]) -> Mf:
    '''Find solutions matching any one of mfs.'''
    return lambda v: lambda c: chain.from_iterable(mf(v)(c) for mf in mfs)


def alt(*mfs:Mf) -> Mf:
    '''Find solutions matching any one of mfs.'''
    return _alt_from_iterable(mfs)

alt.from_iterable = _alt_from_iterable  # type: ignore


class Cut(Exception):
    '''Exception to be caught at the nearest previous prune point.'''


def cut(v:Value) -> Ma:
    '''Jump to the nearest previous prune point.'''
    def _ma(c:Cont) -> Solutions:
        yield from unit(v)(c)
        raise Cut()
    return _ma


def prune(mf:Mf) -> Mf:
    '''Set point to which a cut jumps.'''
    def _mf(v:Value) -> Ma:
        def _ma(c:Cont) -> Solutions:
            try:
                yield from mf(v)(c)
            except Cut:
                yield from ()
        return _ma
    return _mf


def no(mf:Mf) -> Mf:
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    return prune(alt(seq(mf, cut, zero), unit))


def predicate(func:Callable[..., Mf]) -> Callable[..., Mf]:
    '''Helper decorator for backtrackable functions.'''
    # All this does is to add another level of indirection.
    # It is needed to delay the invocation of recursive functions.
    @wraps(func)
    def _(*args, **kwargs):
        return lambda v: func(*args, **kwargs)(v)  # pylint: disable=W0108
    return _
