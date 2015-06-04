Contributing
============

Atramhasis is being developed as open source software by the 
[Flanders Heritage Agency]. All development is done on the agency's 
[Github page for Atramhasis].

Since we place a lot of importance of code quality, we expect to have a good 
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

Every pull request will be run through [Travis-ci]. When providing a pull 
request, please run the unit tests first and make sure they all pass. Please 
provide new unit tests to maintain 100% coverage. If you send us a pull request
and this build doesn't function, please correct the issue at hand or let us 
know why it's not working.

[Flanders Heritage Agency]: https://www.onroerenderfgoed.be
[Github page for Atramhasis]: https://github.com/OnroerendErfgoed/atramhasis
[Travis-ci]: https://travis-ci.org/OnroerendErfgoed/atramhasis
[Coveralls]: https://coveralls.io/r/OnroerendErfgoed/atramhasis
[pytest]: http://pytest.org
[tox]: http://tox.readthedocs.org