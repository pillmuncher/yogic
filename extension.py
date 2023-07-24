# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

''''''

from functools import wraps

def exctension(obj):
    def extension_method(f):
        setattr(obj, f.__name__, f)
    return extension_method
