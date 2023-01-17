Contributing
============

Atramhasis is an open source SKOS editor developed by
[Flanders Heritage Agency]. All development is done on the agency's 
[Github page for Atramhasis]. If you run into bugs or would like to request
a new feature, please open a [Github issue]. Please provide some context to 
your question such as the python and Atramhasis versions you are running. 
If you have specific questions about the software or the datasets hosted at 
[Flanders Heritage Thesaurus] you would rather not address in a public forum, 
please mail <ict@onroerenderfgoed.be>.

If you have some
exerience with Python, Javascript, RDF or SKOS, feel free to contribute
where you can. If you are unsure if a particular change would be welcome, 
create an issue first. When doing so, we recommend you follow these guidelines.

We place a lot of importance on code quality, expect to have a good 
amount of code coverage present and run frequent unit tests. All commits and
pull requests will be tested with [Travis-ci]. Code coverage is being 
monitored with [Coveralls].

Locally you can run unit tests by using [pytest] or [tox]. Running pytest 
manually is good for running a distinct set of unit tests. For a full test run, 
tox is preferred since this can run the unit tests against multiple versions of
python.

```bash
    # Run unit tests for all environments 
    $ tox
    # No coverage
    $ py.test 
    # Coverage
    $ py.test --cov atramhasis --cov-report term-missing
    # Only run a subset of the tests
    $ py.test atramhasis/tests/test_views.py
```

We follow gitflow guidelines for branch naming and merging. Please name your 
branches according to these guidelines:
```
bugfix/<ticketnumber>_description_of_fix
feature/<ticketnumber>_description_of_feature
````

Branches should be branched from develop and merged back into develop once approved 
through a pull request.

Every pull request will be run through [Travis-ci]. When providing a pull 
request, please run the unit tests first and make sure they all pass. Please 
provide new unit tests to maintain 100% coverage. If you send us a pull request
that doesn't pass all tests, please correct the issue at hand or let us 
know why it's not working.

[Flanders Heritage Agency]: https://www.onroerenderfgoed.be
[Flanders Heritage Thesaurus]: https://thesaurus.onroerenderfgoed.be
[Github page for Atramhasis]: https://github.com/OnroerendErfgoed/atramhasis
[Github issue]: https://github.com/OnroerendErfgoed/atramhasis/issues
[Travis-ci]: https://travis-ci.org/OnroerendErfgoed/atramhasis
[Coveralls]: https://coveralls.io/r/OnroerendErfgoed/atramhasis
[pytest]: http://pytest.org
[tox]: http://tox.readthedocs.org
