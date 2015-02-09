0.5.0 (??-??-2015)
------------------

- A conceptscheme, concept or collection can now be export to RDF through 
  skosprovider_rdf_ 0.3.1. These are individuals export endpoints that can
  be reached in one of two ways. Either by hitting a url like 
  http://localhost:6543/conceptschemes/GEOGRAPHY/c/335 with a supported RDF mimetype
  (``application/rdf+xml``, ``application/x-turtle``, ``text-turle``). Or by
  using an RDF syntax specific suffix (.rdf or .ttl).
- Allow sorting the languages in the admin interface.
- When importing, allow the user to request more information on a concept or
  collection, before actually importing it.
- Reorganised and extended the right click menu on the grid in the admin 
  interface.
- Allow looking up a *skos:match* from within the admin interface.
- Some issues with the length of language ids were solved.
- Fixed some issues when importing a collection instead of a concept.
- Some code cleanup and reorganisation.

0.4.0 (23-12-2014)
------------------

- Update to skosprovider_ 0.5.0. Among other things, this makes it possible
  to handle relations between Concepts and Collections using the 
  *subordinate_arrays* and *superordinates* properties. Conceptschemes are
  now also much better integrated within the providers, thus making it 
  possible to provider more context for a Concept. This version of 
  skosprovider_ can also handle *skos:matches*.
- Add possibility to edit language tags. It's now possible to use the admin
  interface to add, edit and delete languages in Atramhasis. 
- When the REST service receives labels or notes in currently unavailable 
  languages, it will validate those through language_tags_. It the languages 
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
  makes it possible to import Concepts from eg. the AAT (via skosprovider_getty_),
  Flanders Heritage Thesauri (via skosprovider_oe_),
  English Heritage Thesauri (via skosprovider_heritagedata_) or any other 
  SKOS vocabulary for which a skosprovider_ has been written. Currently only 
  the concept or collection itself can be imported, without its relations to 
  other concepts or collections.
- Add the ability to have a delete of a concept or collection fail if it is 
  being used in other systems.
- Implement a delete permission.
- Add validation rule that a Concept must have at least one label.
- Update to skosprovider_sqlalchemy_ 0.4.1.
- Update to pyramid_skosprovider_ 0.5.0.
- Update to skosprovider_rdf_ 0.3.0. This update adds support for dumping 
  ConceptScheme in an RDF file and also handles *subordinate_arrays* and
  *superordinates*.
- Update to language_tags_ 0.3.0.


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
.. _skosprovider_oe: https://github.com/koenedaele/skosprovider_oe
.. _skosprovider_heritagedata: http://skosprovider-heritagedata.readthedocs.org
.. _pyramid_skosprovider: http://pyramid-skosprovider.readthedocs.org
.. _language_tags: http://language-tags.readthedocs.org
