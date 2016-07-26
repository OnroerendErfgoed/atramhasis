.. _services:

=====================
Service Documentation
=====================

This library takes your skosproviders and makes them available as REST services.
The pyramid_skosprovider serves JSON as a REST service so it can be used
easily inside a AJAX webbrowser call or by an external program.

The following API can be used by clients:

.. http:get:: /uris
    :synopsis: Look up where a certain URI can be found.

    Find more information on a certain :term:`URI`. This can map to eiter
    a concept, collection or conceptscheme that is known by the current SKOS
    registry.

    **Example request**:

    .. sourcecode:: http

        GET /uris?uri=urn:x-skosprovider:trees HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8

        {
            "id": "TREES",
            "uri": "urn:x-skosprovider:trees",
            "type": "concept_scheme"
        }

    **Example request**:

    .. sourcecode:: http

        GET /uris/?uri=http://python.com/trees/larch HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8

        {
            "id": "1",
            "uri": "http://python.com/trees/larch",
            "type": "concept",
            "concept_scheme": {
                "id": "TREES",
                "uri": "urn:x-skosprovider:trees"
            }
        }

    :query uri: The URI to search for.

    :statuscode 200: The URI maps to something known by pyramid_skosprovider,
        either a conceptscheme, a concept or collection.
    :statuscode 404: The URI can't be found by pyramid_skosprovider.

.. http:get:: /c
    :synopsis: Search concepts or collections.

    Search for concepts or collections, no matter what scheme they're a part of.

    Although it is possible to search a single conceptscheme with just this
    endpoint, for performance reasons it is advised to use
    :http:get:`/conceptschemes/{scheme_id}/c`.

    **Example request**:

    .. sourcecode:: http

        GET /c HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Range:  items 0-2/232
        Content-Type:  application/json; charset=UTF-8

        [
            {
                "id": "1",
                "uri": "urn:x-skosprovider:TREES:1",
                "type": "concept",
                "label": "De Lariks"
            }, {
                "id": "2",
                "uri": "urn:x-skosprovider:TREES:2",
                "type": "concept",
                "label": "De Paardekastanje"
            }, {
                "id": 3,
                "uri": "urn:x-skosprovider:TREES:3",
                "type": "collection",
                "label": "Bomen per soort"
            }
        ]

    **Example request**:

    .. sourcecode:: http

        GET /c?type=concept&providers.subject=external&sort=uri HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    :query type: Define if you want to show concepts or collections. Leave
        blank to show both.
    :query mode: Allows for special processing mode for dijitFilteringSelect.
        Makes it possible to use wildcards in the label parameter.
    :query label: Shows all concepts and collections that have this search
        string in one of their labels.
    :query language: Returns the label with the corresponding language-tag if present.
        If the language is not present for this concept/collection, it falls back to
        1) the default language of the provider. 2) 'en' 3) any label.
        Eg. ``?language=nl`` to show the dutch labels of the concepts/collections.
    :query sort: Define if you want to sort the results by a given field. Otherwise items are returned
        in an indeterminate order. Prefix with '+' to sort ascending, '-' to sort descending.
        eg. ``?sort=-label`` to sort all results descending by label.
    :query providers.ids: A comma separated list of concept scheme id's. The query
        will only be passed to the providers with these id's. eg.
        ``?providers.ids=TREES, PARROTS`` will only list concepts from these two providers.
    :query providers.subject: A subject can be registered with a skosprovider in
        the registry. Adding this search parameter means that the query will only
        be passed on to providers that have been tagged with this subject. Eg.
        ``?providers.subject=external`` to only query the providers that have been marked
        with the subject `external`.

    :reqheader Range: Can be used to request a certain set of results.
        eg. ``items=0-24`` requests the first 25 results.
    :resheader Content-Range: Tells the client what set of results is being returned
        eg. ``items=0-24/306`` means the first 25 out of 306 results are being returned.

    :statuscode 200: The concepts in this conceptscheme were found.

.. http:get:: /conceptschemes
    :synopsis: Get all registered conceptschemes.

    Get all registered conceptschemes.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:42:34 GMT

        [
            {
                "id": "TREES",
                "uri": "urn:x-skosprovider:trees",
                "label": "Different types of trees."
            }
        ]


    :statuscode 200: The list of conceptschemes was found.


.. http:get:: /conceptschemes/{scheme_id}
    :synopsis: Get information about a concept scheme.

    Get information about a concept scheme.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Length:  15
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:45:37 GMT
        Server:  waitress

        {
            "id": "TREES",
            "uri": "urn:x-skosprovider:trees",
            "label": "Different types of trees.",
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "Different types of trees."},
                {"type": "prefLabel", "language": "nl", "label": "Verschillende soorten bomen."}
            ]
        }

    **Example request**:

    -.. sourcecode:: http

        GET /conceptschemes/PLANTS HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Content-Length:  775
        Content-Type:  text/html; charset=UTF-8
        Date:  Tue, 15 Apr 2014 20:32:52 GMT
        Server:  waitress

    :statuscode 200: The conceptscheme was found.
    :statuscode 404: The conceptscheme was not found.

.. http:get:: /conceptschemes/{scheme_id}/topconcepts
    :synopsis: Get the top concepts in a scheme.

    Get all top concepts in a certain conceptscheme. These are all the concepts
    in the conceptscheme that have no broader concept.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/topconcepts HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:47:33 GMT
        Server:  waitress

        [
            {
                "id": "1",
                "uri": "urn:x-skosprovider:TREES:1",
                "type": "concept",
                "label": "De Lariks"
            }, {
                "id": "2",
                "uri": "urn:x-skosprovider:TREES:2",
                "type": "concept",
                "label": "De Paardekastanje"
            }
        ]

    :query language: Returns the label with the corresponding language-tag if present.
        If the language is not present for this concept/collection, it falls back to
        1) the default language of the provider. 2) 'en' 3) any label.
        Eg. ``?language=nl`` to show the dutch labels of the concepts/collections.

    :statuscode 200: The topconcepts in this conceptscheme were found.
    :statuscode 404: The conceptscheme was not found.

.. http:get:: /conceptschemes/{scheme_id}/displaytop
    :synopsis: Get the top of a display hierarchy.

    Get the top of a display hierarchy. Depending on the underlying provider
    this will be a list of Concepts and Collections.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/displaytop HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:47:33 GMT
        Server:  waitress

        [
            {
                "id": "1",
                "uri": "urn:x-skosprovider:TREES:1",
                "type": "concept",
                "label": "De Lariks"
            }, {
                "id": "2",
                "uri": "urn:x-skosprovider:TREES:2",
                "type": "concept",
                "label": "De Paardekastanje"
            }
        ]

    :query language: Returns the label with the corresponding language-tag if present.
        If the language is not present for this concept/collection, it falls back to
        1) the default language of the provider. 2) 'en' 3) any label.
        Eg. ``?language=nl`` to show the dutch labels of the concepts/collections.

    :statuscode 200: The concepts and collections were found.
    :statuscode 404: The conceptscheme was not found.

.. http:get:: /conceptschemes/{scheme_id}/c
    :synopsis: Search for concepts or collections in a scheme.

    Search for concepts or collections in a scheme.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/c HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Length:  117
        Content-Range:  items 0-2/3
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:47:33 GMT
        Server:  waitress

        [
            {
                "id": "1",
                "uri": "urn:x-skosprovider:TREES:1",
                "type": "concept",
                "label": "De Lariks"
            }, {
                "id": "2",
                "uri": "urn:x-skosprovider:TREES:2",
                "type": "concept",
                "label": "De Paardekastanje"
            }, {
                "id": 3,
                "uri": "urn:x-skosprovider:TREES:3",
                "type": "collection",
                "label": "Bomen per soort"
            }
        ]

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/PLANTS/c HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Content-Length:  775
        Content-Type:  text/html; charset=UTF-8
        Date:  Tue, 15 Apr 2014 20:32:52 GMT
        Server:  waitress

    :query type: Define if you want to show concepts or collections. Leave
        blank to show both.
    :query mode: Allows for special processing mode for dijitFilteringSelect.
        Makes it possible to use wildcards in the label parameter.
    :query label: Shows all concepts and collections that have this search
        string in one of their labels.
    :query collection: Get information about the content of a collection.
        Expects to be passed an id of a collection in this scheme. Will restrict
        the search to concepts or collections that are a member of this collection
        or a narrower concept of a member.
    :query language: Returns the label with the corresponding language-tag if present.
        If the language is not present for this concept/collection, it falls back to
        1) the default language of the provider. 2) 'en' 3) any label.
        Eg. ``?language=nl`` to show the dutch labels of the concepts/collections.
    :query sort: Define if you want to sort the results by a given field. Otherwise items are returned
        in an indeterminate order. Prefix with '+' to sort ascending, '-' to sort descending.
        eg. ``?sort=-label`` to sort all results descending by label.

    :reqheader Range: Can be used to request a certain set of results.
        eg. ``items=0-24`` requests the first 25 results.
    :resheader Content-Range: Tells the client was set of results is being returned
        eg. ``items=0-24/306`` means the first 25 out of 306 results are being returned.
    :statuscode 200: The concepts in this conceptscheme were found.
    :statuscode 404: The conceptscheme was not found.

.. http:get:: /conceptschemes/{scheme_id}/c/{c_id}
    :synopsis: Get information about a concept or collection.

    Get information about a concept or collection.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/c/1 HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        Date: Mon, 14 Apr 2014 14:49:27 GMT
        Server: waitress

        {
            "broader": [],
            "narrower": [],
            "notes": [
                {"note": "A type of tree.", "type": "definition", "language": "en"}
            ],
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "The Larch"},
                {"type": "prefLabel", "language": "nl", "label": "De Lariks"}
            ],
            "type": "concept",
            "id": "1",
            "uri": "urn:x-skosprovider:TREES:1",
            "related": [],
            "label": "The Larch",
            "matches": {
                "close": [
                    "http://id.python.org/different/types/of/trees/nr/1/the/larch"
                ]
            },
            "concept_scheme": {
                "uri": "urn:x-foo:bar"
            }
        }

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/c/4 HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Content-Length:  775
        Content-Type:  text/html; charset=UTF-8
        Date:  Tue, 15 Apr 2014 20:06:12 GMT
        Server:  waitress

    :statuscode 200: The concept was found in the conceptscheme.
    :statuscode 404: The concept was not found in the conceptscheme or the
        conceptscheme was not found.


.. http:get:: /conceptschemes/{scheme_id}/c/{c_id}/displaychildren
    :synopsis: Get the children for display purposes.

    Get a list of Collections and Concepts that should be displayed as
    children of this Concept or Collection.

    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/c/3/displaychildren HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:49:27 GMT
        Server:  waitress

        [
            {
                "id": "1",
                "uri": "urn:x-skosprovider:TREES:1",
                "type": "concept",
                "label": "De Lariks"
            }, {
                "id": "2",
                "uri": "urn:x-skosprovider:TREES:2",
                "type": "concept",
                "label": "De Paardekastanje"
            }
        ]

    :query language: Returns the label with the corresponding language-tag if present.
        If the language is not present for this concept/collection, it falls back to
        1) the default language of the provider. 2) 'en' 3) any label.
        Eg. ``?language=nl`` to show the dutch labels of the concepts/collections.

    :statuscode 200: The concept was found in the conceptscheme.
    :statuscode 404: The concept was not found in the conceptscheme or the
        conceptscheme was not found.


.. http:get:: /conceptschemes/{scheme_id}/c/{c_id}/expand
    :synopsis: Expand a concept or collection to all it's narrower concepts.

    Expand a concept or collection to all it's narrower
    concepts.

    This method should recurse and also return narrower concepts
    of narrower concepts.

    If the id passed belongs to a :class:`skosprovider.skos.Concept`,
    the id of the concept itself should be include in the return value.

    If the id passed belongs to a :class:`skosprovider.skos.Collection`,
    the id of the collection itself must not be present in the return value
    In this case the return value includes all the member concepts and
    their narrower concepts.

    Returns A list of id's or :class:`HTTPNotFound` if the concept or collection doesn't
        exist.


    **Example request**:

    .. sourcecode:: http

        GET /conceptschemes/TREES/c/3/expand HTTP/1.1
        Host: localhost:6543
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type:  application/json; charset=UTF-8
        Date:  Mon, 14 Apr 2014 14:49:27 GMT
        Server:  waitress

        [1 , 2]

    :statuscode 200: The concept/collection was found in the conceptscheme.
    :statuscode 404: The concept/collection was not found in the conceptscheme or the
        conceptscheme was not found.
