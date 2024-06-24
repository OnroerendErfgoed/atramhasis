Contributing
============

Atramhasis is an open source SKOS editor developed by [Flanders Heritage].
Consult the [Atramhasis documentation] for more information. All development 
is done through our [Github page for Atramhasis]. If you run into bugs or 
would like to request a new feature, please open a [Github issue]. Please 
provide some context to your question such as the operating system, 
Python and Atramhasis versions you are running. If you have specific questions 
about the software or the datasets hosted at [Flanders Heritage Thesaurus] 
you would rather not address in a public forum, please mail us at 
<ict@onroerenderfgoed.be>.

If you have some
exerience with Python, Javascript, RDF or SKOS, feel free to contribute
where you can. If you are unsure if a particular change would be welcome, 
create a [Github issue] first. When doing so, we recommend you follow these 
guidelines.

Please setup a local installation according to the [development guidelines] in
our online documentation, especially if you are looking to make a major 
contribution. For certain changes, such as updating a part of the documentation 
this is not necessary.

We place a lot of importance on code quality, expect to have a good 
amount of code coverage present and run frequent unit tests.
Code coverage is being monitored with [Coveralls].

Locally you can run unit tests by using [pytest].

```bash
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

Feature and bugfix branches should be branched from develop and will be merged 
back into develop once approved through a pull request.

All commits and pull requests will be automatically tested using 
[GitHub Actions workflows]. When providing a pull request, please run 
the unit tests first and make sure they all pass. Please provide new unit tests
to maintain 100% coverage. If you send us a pull request
that doesn't pass all tests, please correct the issue at hand or let us 
know why it's not working.

[Flanders Heritage]: https://www.onroerenderfgoed.be
[Atramhasis documentation]: https://atramhasis.readthedocs.io/en/latest
[Flanders Heritage Thesaurus]: https://thesaurus.onroerenderfgoed.be
[Github page for Atramhasis]: https://github.com/OnroerendErfgoed/atramhasis
[Github issue]: https://github.com/OnroerendErfgoed/atramhasis/issues
[development guidelines]: https://atramhasis.readthedocs.io/en/latest/development.html
[Coveralls]: https://coveralls.io/r/OnroerendErfgoed/atramhasis
[pytest]: http://pytest.org
[GitHub Actions workflows]: https://github.com/OnroerendErfgoed/atramhasis/actions
