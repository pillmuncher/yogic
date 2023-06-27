# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__date__ = '2023-06-26'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'bind',
    'unit',
    'zero',
    'no',
    'then',
    'alt',
    'seq',
    'run',
    'predicate',
    'resolve',
    'unify',
    'var',
)

from collections import namedtuple, ChainMap
from collections.abc import Mapping
from functools import wraps, reduce
from itertools import count, chain
from . import _version
__version__ = _version.get_versions()['version']


# A monad for backtracking. Hence it's called the Backtracking Monad.
# Actually, it's just the Continuation Monad wrapped around the List Monad.


def bind(ma, mf):
    '''Return the result of applying mf to ma.'''
    return lambda c: ma(lambda v: mf(v)(c))


def unit(v):
    '''Take the single value v into the monad. Represents success.'''
    return lambda c: c(v)


def zero(v):
    '''Ignore the value v and return an 'empty' monad. Represents failure.'''
    return lambda c: ()


def no(mf):
    '''Invert the result of a monadic computation, AKA negation as failure.'''
    def _(v):
        def __(c):
            for result in mf(v)(c):
                # If at least one solution is found, fail immediately:
                return zero(v)(c)
            else:
                # If no solution is found, succeed:
                return unit(v)(c)
        return __
    return _


def then(mf, mg):
    '''Apply two monadic functions mf and mg in sequence.
    Together with unit, this makes the monad also a monoid.'''
    return lambda v: bind(mf(v), mg)


def _alt_from_iterable(mfs):
    '''Find solutions matching any one of mfs.'''
    return lambda v: lambda c: chain.from_iterable(mf(v)(c) for mf in mfs)


def alt(*mfs):
    '''Find solutions matching any one of mfs.'''
    return _alt_from_iterable(mfs)

alt.from_iterable = _alt_from_iterable


def _seq_from_iterable(mfs):
    '''Find solutions matching all mfs.'''
    return reduce(then, mfs, unit)


def seq(*mfs):
    '''Find solutions matching all mfs.'''
    return _seq_from_iterable(mfs)

seq.from_iterable = _seq_from_iterable


def run(ma):
    '''Start the monadic computation of ma.'''
    return ma(lambda v: (yield v))


# Variable objects to be bound to values in a monadic computation:
Variable = namedtuple('Variable', 'id')
_var_counter = count()


def var():
    '''Helper function to create Variables.'''
    return Variable(next(_var_counter))


class Subst(ChainMap):
    '''An environment that maps Variables to the values they are bound to during
    a monadic computation.'''

    def chase(self, obj):
        '''Chase down Variable bindings.'''
        match obj:
            case Variable() as variable:
                if variable in self:
                    return self.chase(self[variable])
                else:
                    return variable
            case list() | tuple() as sequence:
                return type(sequence)(self.chase(each) for each in sequence)
            case _:
                return obj

    @property
    class proxy(Mapping):
        '''A proxy interface to Subst.'''
        def __init__(self, subst):
            self._subst = subst
        def __getitem__(self, var):
            return self._subst.chase(var)
        def __iter__(self):
            return iter(self._subst)
        def __len__(self):
            return len(self._subst)


def _unify(this, that):
    # Unify two objects in a Subst:
    match this, that:
        case Variable(), object():
            # Bind a Variable to another object:
            if this is that:
                # a Variable, already bound or not, is always bound to itself:
                return unit
            else:
                # bind this to that while creating a new choice point:
                return lambda subst: unit(subst.new_child({this: that}))
        case object(), Variable():
            # Same as above, but with swapped arguments:
            return _unify(that, this)
        case list() | tuple(), list() | tuple():
            # Recursively unify two lists or tuples:
            if type(this) == type(that) and len(this) == len(that):
                return seq.from_iterable(map(unify, this, that))
            else:
                return zero
        case _:
            # Unify other objects only if they're equal:
            if this == that:
                return unit
            else:
                return zero


# Public interface to _unify:
def unify(this, that):
    '''Unify 'this' and 'that'.
    If at least one is an unbound Variable, bind it to the other object.
    If both are either lists or tuples, try to unify them recursively.
    Otherwise, unify them if they are equal.'''
    return lambda subst: _unify(subst.chase(this), subst.chase(that))(subst)


def predicate(func):
    '''Helper decorator for yogic functions.'''
    @wraps(func)
    def _(*args, **kwargs):
        return lambda subst: func(*args, **kwargs)(subst)
    return _


def resolve(goal):
    '''Start the logical resolution of 'goal'. Return all solutions.'''
    return (subst.proxy for subst in run(goal(Subst())))
