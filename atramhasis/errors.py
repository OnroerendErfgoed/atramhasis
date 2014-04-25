class SkosRegistryNotFoundException(Exception):
    def __init__(self, value='No SKOS registry found, please check your application setup'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidJsonException(Exception):
    def __init__(self, value='Content provided doesn\'t contain valid JSON'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConceptSchemeNotFoundException(Exception):
    def __init__(self, scheme_id):
        self.value = 'No conteptscheme found with the given id ' + scheme_id

    def __str__(self):
        return repr(self.value)


class ValidationError(Exception):
    def __init__(self, value, errors):
        self.value = value
        self.errors = errors

    def __str__(self):
        return repr(self.value)