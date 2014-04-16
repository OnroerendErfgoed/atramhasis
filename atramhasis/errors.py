class SkosRegistryNotFoundException(Exception):
    def __init__(self, value='No SKOS registry found, please check your application setup'):
        self.value = value

    def __str__(self):
        return repr(self.value)
