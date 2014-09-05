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
.. _pyramid_skosprovider: http://pyramid-skosprovider.readthedocs.org
