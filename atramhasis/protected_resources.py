# -*- coding: utf-8 -*-
"""
Thid module is used when blocking operations on a certain Concept or Collection
that might be used in external applications.

:versionadded: 0.4.0
"""


class ProtectedResourceEvent(object):
    """
    Event triggered when calling a protected operation on a resource
    """

    def __init__(self, uri):
        self.uri = uri


def protected_operation(fn):
    """
    use this decorator to prevent an operation from being executed
    when the related resource is still in use
    """

    def advice(parent_object, *args, **kw):
        uri = parent_object.request.path_url
        event = ProtectedResourceEvent(uri)
        parent_object.request.registry.notify(event)
        return fn(parent_object, *args, **kw)

    return advice


class ProtectedResourceException(Exception):
    """
    raise this exception when the resource is still used somewhere

    referenced_in should contain locations where the resource is still referenced
    """

    def __init__(self, value, referenced_in):
        self.value = value
        self.referenced_in = referenced_in

    def __str__(self):
        return repr(self.value)
