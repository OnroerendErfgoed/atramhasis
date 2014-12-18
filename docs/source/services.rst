.. _services:

========
Services
========

Read Services
=============

The basic read services are being provided by 
:ref:`Pyramid Skosprovider <pyramidskosprovider:services>`.

Write Services
==============

.. http:post:: /conceptschemes/{scheme_id}/c

    Add a concept or collection to a conceptscheme. The response body will 
    contain a representation of the concept or collection after is has
    been added to the conceptscheme.

    **Example request**:

    .. sourcecode:: http

        POST /conceptschemes/TREES/c HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

        {
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label": "The Larch"
                }
            ],
            "notes": []
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Location: http://demo.atramhasis.org/conceptschemes/TREES/c/1
        Content-Type: application/json

        {
            "id": 1,
            "uri": "urn:x-atramhasis-demo:TREES:1",
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label": "The Larch"
                }
            ],
            "notes": []
        }

    **Example request**:

    .. sourcecode:: http

        POST /conceptschemes/TAUNTS/c HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

        {
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "tauntLabel",
                    "language": "en-FR",
                    "label": "Your mother was a Hamster!"
                }
            ],
            "notes": []
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Location: http://demo.atramhasis.org/conceptschemes/TREES/c/1
        Content-Type: application/json

        {
            "errors": [
                        {"labels": "Invalid labeltype."},
                        {"labels": "Invalid language."}
                      ],
            "message": "Concept could not be validated"
        }

    :param scheme_id: The identifier for a certain concept scheme.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`
    :resheader Location: The url where the newly added concept or collection
        can be found.

    :statuscode 201: The concept or collection was added succesfully.
    :statuscode 400: The concept or collection could not be added because
        the submitted json was invalid due to eg. validation errors.
    :statuscode 404: The conceptscheme `scheme_id` does not exist.
    :statuscode 405: The concept or collection could not be added because
        the conceptscheme `scheme_id` is a readonly conceptscheme.

.. http:put:: /conceptschemes/{scheme_id}/c/{c_id}

    Edit the concept or collection with id `c_id`. The response body will 
    contain a representation of the concept or collection after the 
    modifications.

    **Example request**:

    .. sourcecode:: http

        PUT /conceptschemes/TREES/c/1 HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

        {
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label: "The Larch"
                }, {
                    "type": "prefLabel",
                    "language": "nl",
                    "label": "De Lariks"
                }
            ],
            "notes": []
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": 1,
            "uri": "urn:x-atramhasis-demo:TREES:1",
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label: "The Larch"
                }, {
                    "type": "prefLabel",
                    "language": "nl",
                    "label": "De Lariks"
                }
            ],
            "notes": []
        }

    :param scheme_id: The identifier for a certain concept scheme.
    :param c_id: The identifier for a certain concept or collection.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The concept or collection was edited succesfully.
    :statuscode 400: The concept or collection could not be edited because
        the submitted json was invalid due to eg. validation errors.
    :statuscode 404: The conceptscheme `scheme_id` or 
        the concept or collection `c_id` does not exist.
    :statuscode 405: The concept or collection could not be edited because
        the conceptscheme `scheme_id` is a readonly conceptscheme.

.. http:delete:: /conceptschemes/{scheme_id}/c/{c_id}

    Remove the concept with id `c_id`. The response body will contain the last
    representation known by the service.

    **Example request**:

    .. sourcecode:: http

        DELETE /conceptschemes/TREES/c/1 HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": 1,
            "uri": "urn:x-atramhasis-demo:TREES:1",
            "type": "concept",
            "broader": [],
            "narrower": [],
            "related": [],
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label: "The Larch"
                }, {
                    "type": "prefLabel",
                    "language": "nl",
                    "label": "De Lariks"
                }
            ],
            "notes": []
        }

    :param scheme_id: The identifier for a certain concept scheme.
    :param c_id: The identifier for a certain concept or collection.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The concept or collection was deleted succesfully.
    :statuscode 400: The concept or collection could not be edited because
        the submitted json was invalid due to eg. validation errors.
    :statuscode 404: The conceptscheme `scheme_id` or 
        the concept or collection `c_id` does not exist.
    :statuscode 405: The concept or collection could not be deleted because
        the conceptscheme `scheme_id` is a readonly conceptscheme.
    :statuscode 409: The concept or collection could not be deleted because
        Atramhasis has determined that it's still being used somewhere else. The
        response body will contain a message and a list of :term:`URI`'s that
        are using this concept.
