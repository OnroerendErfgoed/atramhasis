0.5.1 (04-10-2016)
------------------

This minor release fixes a bug with the tree browser. Before it wasn't possible
to zoom and pan the tree. With certain larger trees this would cause issues as
content would run off the page.


0.5.0 (14-09-2016)
------------------

This release is a major update based on the `skosprovider`_ `0.6.0` line
of libraries. The most visible change is with the public and admin interfaces.
These have been completely overhauled to provide a more pleasing user
experience. Among other things visitors are now pointed towards popular concepts
and concepts they have recently visited. Browsing an entire conceptscheme tree
has been redesigned.

The adming interface now offers users an option to edit certain aspects of a
conceptscheme such as the labels, notes and sources. Editing in general has been
update and improved. Links between the public interface and the admin interface
have been added to make switching from one to the other easier. Notes and
sources can now contain certain HTML tags, allowing greater flexibility in
defining concepts and collections.

A command line script was added to make it easy to import an entire
conceptscheme, eg. when migrating from another system. It is now possible to
import a RDF, CSV or JSON file on the command line in your Atramhasis instance.
With earlier versions you had to script this yourself.

As always, bugs have been fixed, code has been rewritten and documenation has
been updated.

See https://github.com/OnroerendErfgoed/atramhasis/milestone/8?closed=1 for the
full list of changes.


0.4.4 (04-06-2015)
------------------

- Added more sample datasets to get a better view of real data. These will make
  the demo more interesting.
- Fix a bug where it was possible to create a relation between a concept and
  itself causing all sorts of nasty things to happen.
- Minor refactoring. Move the pyramid routes to a new file.
- Added a CONTRIBUTING.md file. Contributions welcome!

0.4.3 (11-03-2015)
------------------

We had some packaging issues with the `0.4.2` release.


0.4.2 (11-03-2015)
------------------

This release of Atramhasis is mostly a bugfix update of the `0.4.1` release.

- Fix paths of db in scaffolds
- Add more information on exceptions
- Update skosprovider_getty and skosprovider_heritagedata
  (fix the problems when importing external thesauri)
- Documentation update


0.4.1 (04-03-2015)
------------------

This release of Atramhasis is a minor update of the `0.4.0` release, focussing
on small corrections and improvements and improving the documentation. A few
interesting non-invasive features were added, mostly to the editor's admin
interface and machine-readable exports of RDF data.

Upgrading from `0.4.0` should be simple and cause no or few problems.

- A conceptscheme, concept or collection can now be exported to RDF through
  skosprovider_rdf_ 0.3.1. These are individuals export endpoints that can
  be reached in one of two ways. Either by hitting a url like
  http://localhost:6543/conceptschemes/GEOGRAPHY/c/335 with a supported RDF mimetype
  (``application/rdf+xml``, ``application/x-turtle``, ``text-turle``). Or by
  using an RDF syntax specific suffix (.rdf or .ttl).
- When importing, allow the user to request more information on a concept or
  collection, before actually importing it.
- Allow merging a concept with other concepts it matches. This allows a user to
  compare a local concept with an external one it matches and import any notes
  or labels that are present in the external concept, but not the local one.
- Reworked some parts of the public interface to make everything a bit clearer
  and to make all pages easily reachable.
- Allow sorting the languages in the admin interface.
- Reorganised and extended the right click menu on the grid in the admin
  interface.
- Allow looking up a *skos:match* from within the admin interface.
- Some issues with the length of language ids were solved.
- Fixed some issues when importing a collection instead of a concept.
- Made it easy to add a Google Analytics tracker.
- Added instructions on how to deploy a demo site on heroku_. These work just as
  well for deploying an actual production site to heroku_.
- Lots of small updates and tweaks to the documentation.
- Updated some dependencies.
- Some code cleanup and reorganisation. Several smaller bugs in the admin
  interface were fixed.
- The data fixtures were updated with *skos:note* examples. Added a license for
  reuse of the fixture data.

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
.. _heroku: https://www.heroku.com
