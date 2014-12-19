0.4.0 (???)
-----------

- Update to skosprovider_ 0.5.0. Among other things, this makes it possible
  to handle relations between Concepts and Collections using the 
  *subordinate_arrays* and *superordinates* properties. Conceptschemes are
  now also much better integrated within the providers, thus making it 
  possible to provider more context for a Concept. This version of 
  skosprovider_ can also handle *skos:matches*.
- Add possibility to edit language tags. It's now possible to use the admin
  interface to add, edit and delete languages in Atramhasis. 
- When the REST service receives labels or notes in currently unavailable 
  languages, it will validate those through language_tag_. It the languages 
  are valid according to the IANA registry, they will be added to the languages 
  available in the application.
- Default length of language id changed to 64 characters. This is not available
  as an alembic migration. So only effective when creating a new database.
  If you already have a database created from an older version of Atramhasis,
  please modify accordingly. Modifying column length on SQLite is not possible
  (see http://www.sqlite.org/omitted.html ).
- Abiltity to match Concepts in an Atramhasis ConceptScheme to Concepts in 
  external ConceptSchemes through properties such as *skos:exactMatch* and
  *skos:closeMatch*.
- Ability to import Concepts and Collections from external providers. This 
  makes it possible to import Concepts from eg. the AAT (via skosprovider_getty_) 
  or any other SKOS vocabulary for which a skosprovider_ has been written.
- Implement a delete permission.
- Add validation rule that a Concept must have at least one label.
- Update to skosprovider_sqlalchemy_ 0.4.1.
- Update to pyramid_skosprovider_ 0.5.0.
- Update to skosprovider_rdf_ 0.3.0. This update adds support for dumping 
  ConceptScheme in an RDF file and also handles *subordinate_arrays* and
  *superordinates*.

0.3.1 (05-09-2014)
------------------

- Update to skosprovider_sqlalchemy_ 0.2.1.
- Update to skosprovider_rdf_ 0.1.3 This fixes an issue with RDF having some
  SKOS elements in the wrong namespace. Also added a missing dependency on
  skosprovider_rdf_ to setup.py
- Updated the Travis build file to run a basic dojo build and test for build
  failures.


0.3.0 (15-08-2014)
------------------

- Atramhasis now includes a working admin userinterface at `/admin`. Still needs
  some polish when it comes to error handling and reporting about validation 
  errors.
- The admin module gets run through a dojo build to minimize page loads
  and download times
- Added RDF/XML en RDF/Turtle downloads to the public interface. Currently
  only dumps a full conceptscheme, not individual concepts.
- Added more docs.
  

0.2.0 (16-05-2014)
------------------

- Full public userinterface
- REST CRUD service
- Security integration
- CSV export
- demo using Mozilla Persona as sample security setup


0.1.0 (22-04-2014)
------------------

- Initial version
- Setup of the project: docs, unit testing, code coverage
- Scaffolding for demo and deployment packages
- Limited public user interface
- Basis i18n abilities present
- Integration of pyramid_skosprovider_
- Integration of skosprovider_
- Integration of skosprovider_sqlalchemy_

.. _skosprovider: http://skosprovider.readthedocs.org
.. _skosprovider_sqlalchemy: http://skosprovider-sqlalchemy.readthedocs.org
.. _skosprovider_rdf: http://skosprovider-rdf.readthedocs.org
.. _skosprovider_getty: http://skosprovider-getty.readthedocs.org
.. _pyramid_skosprovider: http://pyramid-skosprovider.readthedocs.org
.. _language_tag: http://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
