.. _services:

========
Services
========

Atramhasis can be used fully with a :term:`SOA`. While we provide a public and
and an administrator's interface out of the box, you can also write your own client
side code that interacts with the Atramhasis services, either for reading 
information or writing it.

While this chapter provides more narrative documentation on the services available,
the most up to date version of the API can be accessed through the `online API docs 
at the Flander Heritage Thesaurus <https://thesaurus.onroerenderfgoed.be/api_doc>`_
or in your local version at `/api_doc`.

Pyramid_skosprovider
====================

.. include:: ../external/pyramid_skosprovider/services.rst
   :start-line: 5

Atramhasis
==========

Concepts and collections
------------------------

The main Atramhasis write services allow you to add concepts and collections,
edit them and delete them.

.. http:post:: /conceptschemes/{scheme_id}/c

    Add a concept or collection to a conceptscheme. The response body will 
    contain a representation of the concept or collection after is has
    been added to the conceptscheme.

    **Example request**:

    .. sourcecode:: http

        POST /conceptschemes/TREES/c HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json
        Content-Type: application/json

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
        Content-Type: application/json

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
        Content-Type: application/json

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
                    "label": "The Larch"
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
                    "label": "The Larch"
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

Languages
---------

Apart from the main services, Atramhasis exposes some secondary services that
deal with languages.

.. http:get:: /languages

    List all languages known to this Atramhasis instance.

    Please bear in mind that these are not all known IANA language tags, but a
    subset used in this Atramhasis instance. This is used to populate drop down
    lists and such.

    **Example request**:

    .. sourcecode:: http

        GET /languages HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        [
            {"id": "la", "name": "Latin"},
            {"id": "nl", "name": "Dutch"},
            {"id": "en", "name": "English"},
            {"id": "fr", "name": "French"},
            {"id": "de", "name": "German"}
        ]

    :param sort: Which field to sort on. Use `-` and `+` to indicate sort order.
        Eg. `id` or `+id` sort ascending on `id`, `-name` sort descending on
        `name`.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The list of languages was returned.

.. http:get:: /languages/{language_id}

    Get information on a certain language.

    Please bear in mind this will only work for languages known to this
    Atramhasis instance. Valid IANA languages not known to this instance will
    not work.

    **Example request**:

    .. sourcecode:: http

        GET /languages HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": "la",
            "name": "Latin"
        }

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The language was found.
    :statuscode 404: The language was not found in this instance.

.. http:put:: /languages/{language_id}

    Update the information on a certain language or create an entry for a new
    one.

    The user is required to submit the `language_id` and this must be a valid
    IANA language tag.

    **Example request**:

    .. sourcecode:: http

        PUT /languages/nl-BE HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json
        Content-Type: application/json

        {
            "id": "nl-BE",
            "name": "Dutch (Flanders)"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": "nl-BE",
            "name": "Dutch (Flanders)"
        }

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The language was updated or added.
    :statuscode 400: The request could not be executed because of problems with
        the submitted data. Most likely you are submitting an invalid IANA
        langage code.

.. http:delete:: /languages/{language_id}

    Delete a language from this Atramhasis instance.

    **Example request**:

    .. sourcecode:: http

        DELETE /languages/nl-BE HTTP/1.1
        Host: demo.atramhasis.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": "nl-BE",
            "name": "Dutch (Flanders)"
        }

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The language was deleted.
    :statuscode 404: The language was not found in this instance.
