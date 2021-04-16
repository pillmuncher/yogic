# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.20a'
__date__ = '2021-04-16'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

__all__ = (
    'multimethod',
)

from collections import defaultdict
from functools import wraps
from inspect import signature, Signature


def multimethod(function, *, _registry=defaultdict(list)):
    '''Provide multimethods to Python, similar to:
    https://www.artima.com/weblogs/viewpost.jsp?thread=101605'''
    _registry[function.__name__].append((
        function,
        tuple(object if sig.annotation is Signature.empty else sig.annotation
              for sig in signature(function).parameters.values())))
    @wraps(function)
    def _(*args, **kwargs):
        for func, types in _registry[function.__name__]:
            if len(args) == len(types):
                if all(map(isinstance, args, types)):
                    return func(*args, **kwargs)
        raise TypeError("multimethod couldn't find matching function!")
    return _
