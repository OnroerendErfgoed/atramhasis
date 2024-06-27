# -*- coding: utf-8 -*-
from atramhasis.protected_resources import ProtectedResourceEvent
from atramhasis.protected_resources import ProtectedResourceException
from pyramid.events import subscriber


@subscriber(ProtectedResourceEvent)
def sample_impl(event):
    if event.uri.endswith("2"):
        referenced_in = ["urn:someobject", "http://test.test.org/object/2"]
        raise ProtectedResourceException(
            "resource {0} is still in use, preventing operation".format(event.uri),
            referenced_in,
        )
