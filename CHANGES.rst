2.1.0 (4-07-2023)
------------------

- Migrated from setup.py to the hatchling build tool for improved packaging and distribution (#854).
  Benefits include faster builds, modern configuration, and enhanced flexibility for future enhancements.
- Integrate Cookiecutter Projects into Atramhasis for Improved Maintainability and Centralization (#876)


2.0.0 (22-12-2023)
------------------

The final release of version 2.0.0 is very similar to the pre-release. Please read the
notes for that version and be mindful when updating from an older version. You will 
need to migrate some of your configuration to your database as described in
our documentation.

- Added a configuration file for ReadTheDocs. (#846)
- Initializedb script now generates providers in the database, where before they were 
  created in code and then migrated. (#848)
- Update skosprovider_getty to get more robust services when dealing with the
  conceptscheme.


2.0.0b1 (17-06-2023)
--------------------

**This is a pre-release of version of 2.0.0**

Atramhasis 2.0.0 is a new major release with some new features and some backwards
incompatible changes that require a careful upgrade and some manual
intervention. Lots of dependencies have been updated, so please test and
evaluate your own integration carefully before updating a production version.

This version provides two major new features:

- It is now possible to have non-numeric identifiers for concepts and collections. 
  The current default (numeric ids) is still supported, but we've made it 
  possible to also use a UUID or assign one manually upon creation of a 
  concept. (#732)
- Creation of providers used to be done with a little bit of code, but is now
  handled through the UI. A thesaurus administrator can be allowed to create new
  conceptschemes by configuring a few parameter such as a URI pattern, a 
  provider ID, what type of identifiers to use (numeric, guid or manual) 
  and the provider's default language. We have provided a script for upgrading
  an installation that was created for an older version of Atramhasis. Please
  consult our documentation for instructions how to use it. (#744)

Minor features added and bugs fixed:

- Atramhasis is now tested on Python 3.11, 3.10 and 3.9. Support for older 
  versions has been removed.
- Jinja2 3.x is now the expected template engine. Users who have overridden and
  customised many templates might need to update them. (#747)
- Easier and more flexible configuration of analytics snippets, such as 
  `Plausible Analytics <https://plausible.io>`_. (#738)
- Refactoring of the import from file script, to avoid duplicate code and avoid
  creating duplicate labels. (#818)
- Update label of default language `vls` to `Vlaams` to be inline with the normal 
  IANA label. (#767)
- Update language-tags to latest version. (#754)
- Stop building universal wheels (#752)
- Minor refactoring of view method to get publically available conceptschemes (#777)

1.3.2 (14-03-2023)
------------------

- Fix broken CITATION.cff file. Otherwise this version is identical to 1.3.1

1.3.1 (14-03-2023)
------------------

- Show actual language tags in admin interface drop downs, as opposed to just the labels to reduce confusion. (#766)
- JSON-LD export was broken because the provided context was missing a context 
  attribute. (#794)
- Added a link from a concept page in the admin interface to the public interface. (#791)
- Saving a concept in the admin interface triggers a reload of the list view. (#763)
- Fix notation of JSON-LD. (#792)
- Update docs to no longer reference mkvirtualenv, use standard venv instead (#773)
- Update CONTRIBUTING.md file (#756)
- Remove unneeded references to pytz (#780, #796)

1.3.0 (04-01-2023)
-------------------

- Fix some dependencies to avoid broken dependencies (#749)
- Remove Waitress from setup.py since this it's not necessary to run in production with Waitress (#749)
- Update skosprovider_rdf to version 1.3.0 to avoid accidentally 
  exposing URI's as dcterms:identifier. (#741)

1.2.0 (19-10-2022)
------------------

- Concept detail RDF is missing link with collection (#707)
- import_data.py: NameError: name 'Note' is not defined (#721)
- Better error logging for dump_rdf script (#712)
- Upgrade to rdflib 6 (#714)
- 500 Exception when using unexpected values for endpoint /conceptschemes/[schemeid]/c/[concept_id] (#708)

1.1.0 (04-07-2022)
------------------

- Integration with LDF is out of date (#687)
- Missing dependency pyramid_openapi3 (#697)
- Docs should be updated for creating a demo site (#699)
- Demo site crashes on a concept detail (#700)


1.0.3 (14-01-2022)
------------------

- Update skosprovider to fix language queryparameter: https://github.com/OnroerendErfgoed/skosprovider/releases/tag/1.1.1


1.0.2 (06-01-2022)
------------------

- Keep uri field when change concept type: uri field is set to null in database when we change the type of a concept (#680)
- Not possible to save notes within a collection via the UI (#682)
- Add 2 references (article and software) to CITATION.cff file.


1.0.1 (04-01-2022)
------------------

1.0.0 was a brown bag release. Sorry!

This version is exactly the same as 1.0.0, but properly packaged.


1.0.0 (24-12-2021)
------------------
Python 2 support was dropped in this release

- Upgrade requirements (#653, #648, #654)
- API docs were added and are available via the endpoint /api_docs. They include all atramhasis API services,as well as the API endpoins included from https://github.com/OnroerendErfgoed/pyramid_skosprovider/ (#670)
- The presentation of labels in the Tree view are optimized (#658)
- Fix bug to convert collection to concept (#668)
- Fix bug: Sources not shown on conceptscheme page (#652)
- As a user I want a unified searchparam to search for concepts or collections by type, searchparam type will be used in favor of ctype no matter what output format we are requesting (#651)


0.7.0 (06-11-2020)
------------------

This releases is a new major release with some new features and some backwards
incompatible changes that require a careful upgrade and some manual
intervention. The 0.7.x releases will also be that last to support Python 2. If
you haven't upgraded to Python 3 yet, we advise you to do now.

**BC break** The major change in this version is no longer initiating the
`skosprovider.registry.Registry` on starting the application, but when a
request is created. The previous way of working created problems with
SQLAlchemy providers in a webserver using mutiple threads. Please review the
docs at
https://atramhasis.readthedocs.io/en/latest/customisation.html#creating-conceptschemes
to see how it works now. For more background, have a look at the
pyramid_skosprovider_ docs at https://pyramid-skosprovider.readthedocs.io/en/0.9.0/install.html

- All requirements were updated to their latest versions. Python versions were
  fixed to 2.7, 3.6, 3.7 and 3.8. If you made custom changes, you might have to
  edit them. (#508, #519, #513, #566)
- Npm has replaced bower as the package manager for frontend packages and the
  build process was revised. If you made custom frontend changes, please
  check them thoroughly.(#511)
- Instantiation of the SKOS registry was changed to work on a per request
  basis. (#346, #490, #535)
- Fixed a major issue with generating the expanded version of a concept. By
  default the assumption was that concepts in a collection were also narrower
  concepts of the collection's superordinate concept, but the implementation
  for this was incomplete and contained bugs. This has been changed to an
  boolean attribute `infer_concept_relations`. When set to true, concepts in a
  collection are considerd to be narrower concepts of that collections's
  superordinate concept. This is especially important for a provider's
  `expand` function and affects what is considered a narrower concept of a
  concept that uses `thesaurus arrays` or `node labels`.
- The docs were updated and now contain a part detailing what Atramhasis does
  with some screenshots. (#495, #583, #440)
- Default inclusion of skosprovider_heritagedata was removed because the
  service is unstable too often. (#537)
- Improve some SEO by adding canonicul URL's, open graph info, Twitter cards
  and the ability to generate a sitemap through a script. (#530, #531, #496,
  #497)
- Clean up importing and exporting of conceptschemes to make it easier. (#452,
  #475, #476, #495)
- Provide a simple, printable version of a thesaurus tree. (#533, #532)
- Add a script to make removing a conceptscheme easier. Be careful as this will
  drop all concepts, collections and the conceptscheme itself. (#579)
- Lots of minor improvements and bug fixes.

0.6.7 (21-06-2019)
------------------

- Fix corrupt build
- Security updates

0.6.6 (01-03-2019)
------------------

- Update Colander and other dependencies. (#464)
- Remove old convert_oe script because it depends on an obsolete webservice. (#466)
- Fix an issue with circular dependencies in requirements files. (#463)
- Change the default GA macro to anonymizeIp and be more GDPR compliant. (#450)

0.6.5 (19-12-2018)
------------------

- Generate a default dump location in development.ini files. (#416)
- Update skosprovider_sqlalchemy to solve a problem with the tree cache. (#455)
- Update a lot of dependencies.

0.6.4 (22-12-2017)
------------------

0.6.3 was a brown bag release. Sorry!

This version is exactly the same as 0.6.3, but properly packaged.

0.6.3 (21-12-2017)
------------------

- This version updates a lot of the requirements to their latest versions. This
  might be an issued if you've written lots of code against older pyramid
  versions. (#418, #413, #412, #411, #410, #408, #407, #404, #403)
- Remove authentication from the demo version since Persona does not work
  anymore. (#361)
- Fixed the base HTML template and added a DOCTYPE declaration. (#429)
- Update the URI's for licenses of the Flemish Government. (#430)
- Fixed an issues with sorting on Python 3. (#424)

0.6.2 (11-10-2017)
------------------

- When an LDF server is present, add a link to the HTML document to this server.
  (#394)
- Wrong expansion of SKOS namespace in LDF server. (#401)

0.6.1 (01-09-2017)
------------------

This release is a minor release, containing improvements regarding the Linked
Data Fragments server.

- Also add hidden datasets to the LDF server. Only external ones are not added
  now. (#390)
- Make it possible to set the LDF server protocol when generating the config.
  (#391)
- When generating an LDF server config, add a composite source as well. (#393)
- When generating the dataset information, add hydra controls that link to 
  the LDF server instance. (#392)

0.6.0 (23-08-2017)
------------------

This release is a major release containing new features.

- Added a script to generate nightly dumps. Instead of generating full
  downloads on demand, they can now be generated by a cron job (eg. once per
  night, week, ...). This makes it possible to download a large conceptscheme at
  once. During these dumps, some statistics on every conceptscheme such as the
  number of triples in it will be generated as well. This was done to make it
  easier to embed a custom Python based LDF server, but currently only serves
  the purpose of keeping some score. (#337, #360)
- Added easy integration with a Linked Data Fragments server 
  (https://linkeddatafragments.org). Atramhasis can now
  generate a config file for such a server that you can use to setup the server.
  By default this config will work with the Turtle files that can be generated
  every night. But if you have access to the HDT library, you can also work with
  HDT files for a masssive performance boost. See the section `Running a Linked
  Data Fragments server` in the docs for more information. (#365)
- Add some more information the HTML title tags for a concept detail. (#363)
- Changed the UI for doing a search so that you now get a proper warning when
  searching for a label without specifying the conceptscheme to search in. (#373)
- It is now possible to generate URI's when importing from a file that does not
  contain them, eg. a JSON or CSV file. The `import_file` can now take a
  `pattern_uri` parameter than will be used to generate new URI's with. (#372)
- Fixed some issues with the tree cache that came to light when running
  Atramhasis as two nodes. Where before it was not possible to configure the
  tree cache, it now is. Previously an in-memory cache would always be used. Now
  it's possible to use a different type of cache. If you're running more than
  one webserver, it is advised to run a shared cache. If you're running a
  previous version of Atramhasis, you will need to configure your cache with 
  `cache.tree` and `cache.list` settings. (#371)
- It is now possible to add sortLabels to concepts. These can be used in the
  REST service to arbitrarily sort concepts. The sortLabel works per language.
  This makes it possible to eg. sort historical periods in chronological order.
  Most of the functionality was already present in `skosprovider` 0.6.0, but it
  had not been properly included in Atramhasis.
  (#362)
- Added 'und - undetermined' to the default language set to support json file 
  imports. (#386)
- Fixed a bug when editing concepts where data from previously opened concepts
  would bleed into the concept you were editing. (#367)
- Update several dependencies to the latest versions. (#380, #381, #376)
- Added 'und - undetermined' to the default language set to support json file imports (#386)

0.5.2 (07-10-2016)
------------------

This minor release fixes a bug with the protected resource event. The event should
give the uri of a concept instead of the url path. In addition to the uri the request
is added to the event. It also fixes the bug with removing relations and updates the 
requirements for skosprovider_sqlalchemy_.


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
