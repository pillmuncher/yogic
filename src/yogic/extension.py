# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

"""Provides a utility function to extend objects with additional methods."""


def extend(obj):
    """
    extend(obj)
    Decorator function to add a method to the given object.

    Parameters:
        obj (object): The object to be extended.

    Returns:

        function: A decorator function  that adds the
        decorated function as a method to the object.

    """

    def extension_method(f):
        setattr(obj, f.__name__, f)

    return extension_method
