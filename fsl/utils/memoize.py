#!/usr/bin/env python
#
# memoize.py - Memoization decorators.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides a handful of decorators which may be used to memoize
a function:

 .. autosummary::
    :nosignatures:

    Instanceify
    memoizeMD5
    skipUnchanged
"""


import hashlib
import functools


def memoizeMD5(func):
    """Memoize the given function. Whenever the function is called, an
    md5 digest of its arguments is calculated - if the digest has been
    previously cached, the previous value calculated by the function is
    returned.
    """

    cache = {}

    def wrapper(*args, **kwargs):
        args = list(args) + list(kwargs.values())

        hashobj = hashlib.md5()

        for arg in args:
            hashobj.update(str(arg))

        digest = hashobj.hexdigest()
        cached = cache.get(digest)

        if cached is not None:
            return cached

        result = func(*args, **kwargs)

        cache[digest] = result

        return result

    return wrapper


def skipUnchanged(func):
    """This decorator is intended for use with *setter* functions - a function
     which accepts a name and a value, and is intended to set some named
     attribute to the given value.

    This decorator keeps a cache of name-value pairs. When the decorator is
    called with a specific name and value, the cache is checked and, if the
    given value is the same as the cached value, the decorated function is
    *not* called. If the given value is different from the cached value (or
    there is no value), the decorated function is called.

    .. note:: This decorator ignores the return value of the decorated
              function.

    :returns: ``True`` if the underlying setter function was called, ``False``
              otherwise.
    """

    import numpy as np
    
    cache = {}
    
    def wrapper(name, value, *args, **kwargs):

        oldVal = cache.get(name, None)

        if oldVal is not None:
            
            oldIsArray = isinstance(oldVal, np.ndarray)
            newIsArray = isinstance(value,  np.ndarray)
            isarray    = oldIsArray or newIsArray

            if isarray: nochange = np.all(oldVal == value)
            else:       nochange =        oldVal == value

            if nochange:
                return False 

        func(name, value, *args, **kwargs)

        cache[name] = value

        return True

    return wrapper


class Instanceify(object):
    """This class is intended to be used to decorate other decorators, so they
    can be applied to instance methods. For example, say we have the following
    class::

        class Container(object):

            def __init__(self):
                self.__items = {}

            @skipUnchanged
            def set(self, name, value):
                self.__items[name] = value

    
    Given this definition, a single :func:`skipUnchanged` decorator will be
    created and shared amongst all ``Container`` instances. This is not ideal,
    as the value cache created by the :func:`skipUnchanged` decorator should
    be associated with a single ``Container`` instance.

    
    By redefining the ``Container`` class definition like so::

    
        class Container(object):

            def __init__(self):
                self.__items = {}

            @Instanceify(skipUnchanged)
            def set(self, name, value):
                self.__items[name] = value


    a separate :func:`skipUnchanged` decorator is created for, and associated
    with, every ``Container`` instance.

    
    This is achieved because an ``Instanceify`` instance is a descriptor. When
    first accessed as an instance attribute, an ``Instanceify`` instance will
    create the real decorator function, and replace itself on the instance.
    """

    
    def __init__(self, realDecorator):
        """Create an ``Instanceify`` decorator.

        :arg realDecorator: A reference to the decorator that is to be
                            *instance-ified*.
        """

        self.__realDecorator = realDecorator
        self.__func          = None


    def __call__(self, func):
        """Called immediately after :meth:`__init__`, and passed the method
        that is to be decorated.
        """
        self.__func = func
        return self


    def __get__(self, instance, cls):
        """When an ``Instanceify`` instance is accessed as an attribute of
        another object, it will create the real (instance-ified) decorator,
        and replace itself on the instance with the real decorator.
        """

        if instance is None:
            return self.__func

        method    = functools.partial(self.__func, instance)
        decMethod = self.__realDecorator(method)

        setattr(instance, self.__func.__name__, decMethod)
        return functools.update_wrapper(decMethod, self.__func)