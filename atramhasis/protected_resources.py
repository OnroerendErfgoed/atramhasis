import re

from atramhasis.errors import ConceptSchemeNotFoundException

"""
Thid module is used when blocking operations on a certain Concept or Collection
that might be used in external applications.

:versionadded: 0.4.0
"""


class ProtectedResourceEvent:
    """
    Event triggered when calling a protected operation on a resource
    """

    def __init__(self, uri, request):
        self.uri = uri
        self.request = request


def protected_operation(fn):
    """
    use this decorator to prevent an operation from being executed
    when the related resource is still in use
    """

    def advice(parent_object, *args, **kw):
        request = parent_object.request
        url = request.path
        match = re.compile(r'/conceptschemes/(\w+)/c/(\w+)').match(url)
        scheme_id = match.group(1)
        c_id = match.group(2)
        provider = request.skos_registry.get_provider(scheme_id)
        if not provider:
            raise ConceptSchemeNotFoundException(scheme_id)
        uri = provider.uri_generator.generate(id=c_id)
        event = ProtectedResourceEvent(uri, request)
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
