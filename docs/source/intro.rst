.. _introduction:

Introduction
============

Atramhasis is an online SKOS editor. It allows a user to create and edit an
online thesaurus or vocabulary adhering to the 
`SKOS specification <skos_spec_>`_.

Atramhasis is being developed by the `Flanders Heritage Agency`_, an agency of
the Flemish Government that deals with Archaeology, Monuments and Landscapes.

Technology
----------

Atramhasis is a python_ webapplication that is being developed within the 
pyramid_ framework. Other major technologies used are sqlalchemy_ as the ORM 
and jinja2_ as the templating framework.

Client side the main technologies being used are Zurb Foundation and Dojo toolkit.

While Atramhasis is an editor for creating and editing :term:`SKOS` vocabularies,
it uses other libraries that are more geared towards using a vocabulary in an
application.

* skosprovider_: This library defines a 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>`. This 
  is an abstraction of usefull functionalities an application integrating 
  :term:`SKOS` needs. Different libraries can implement this interface for 
  different datasources. This allows decoupling the interface from the concrete
  implementation. Out of the box this comes with a simple 
  :class:`DictionaryProvider <skosprovider.providers.DictionaryProvider>` that
  serves a vocabulary based on a simple python :class:`dict` as datasource.
* skosprovider_sqlalchemy_: An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `SQLAlchemy <http://www.sqlalchemy.org>`_ backend. This allows
  using a RDBMS for reading, but also writing, :term:`SKOS` concepts.
* pyramid_skosprovider_: A library that integrates pyramid_ and skosprovider_.
  This libraries creates a :class:`skosprovider.registry.Registry` and makes it
  accessible through the :class:`pyramid.request.Request`. Is also exposes a 
  set of readonly :ref:`REST services <pyramidskosprovider:services>` on the 
  registered providers.

.. _skos_spec: http://www.w3.org/TR/skos-reference/
.. _Flanders Heritage Agency: https://www.onroerenderfgoed.be
.. _python: https://wwww.python.org
.. _pyramid: http://www.pylonsproject.org/
.. _sqlalchemy: http://www.sqlalchemy.org
.. _jinja2: http://jinja.pocoo.org
.. _skosprovider: http://skosprovider.readthedocs.org
.. _skosprovider_sqlalchemy: http://skosprovider-sqlalchemy.readthedocs.org
.. _pyramid_skosprovider: http://pyramid-skosprovider.readthedocs.org
