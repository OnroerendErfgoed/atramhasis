# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from atramhasis.protected_resources import ProtectedResourceEvent, ProtectedResourceException


@subscriber(ProtectedResourceEvent)
def sample_impl(event):
    if event.uri.endswith('2'):
        referenced_in = ['urn:someobject', 'http://test.test.org/object/2']
        raise ProtectedResourceException('resource {0} is still in use, preventing operation'.format(event.uri),
                                        referenced_in)