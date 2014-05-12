from pyramid.httpexceptions import HTTPNotFound


class SkosRegistryNotFoundException(Exception):
    def __init__(self, value='No SKOS registry found, please check your application setup'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConceptSchemeNotFoundException(HTTPNotFound):
    def __init__(self, scheme_id):
        self.value = 'No conteptscheme found with the given id ' + scheme_id

    def __str__(self):
        return repr(self.value)


class ConceptNotFoundException(HTTPNotFound):
    def __init__(self, c_id):
        self.value = 'No contept found with the given id ' + c_id

    def __str__(self):
        return repr(self.value)


class ValidationError(Exception):
    def __init__(self, value, errors):
        self.value = value
        self.errors = errors

    def __str__(self):
        return repr(self.value)