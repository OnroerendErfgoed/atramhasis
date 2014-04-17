from pyramid.view import view_config, view_defaults
from skosprovider.skos import Concept
from skosprovider.skos import Collection

from atramhasis.errors import SkosRegistryNotFoundException


@view_defaults(accept='text/html')
class AtramhasisView(object):

    def __init__(self, request):
        self.request = request
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()

    @view_config(route_name='home', renderer='templates/atramhasis.jinja2')
    def home_view(self):
        '''
        This view displays the homepage.

        :param request: A :class:`pyramid.request.Request`
        '''
        conceptschemes = [x.get_metadata() for x in self.skos_registry.get_providers()]
        return {'project': 'atramhasis', 'conceptschemes': conceptschemes}


    @view_config(route_name='foundation', renderer='templates/foundation.jinja2')
    def foundation_view(self):
        self.home_view()


    @view_config(route_name='concept', renderer='templates/concept.jinja2')
    def concept_view(self):
        '''
        This view displays the concept details

        :param request: A :class:`pyramid.request.Request`
        '''
        scheme_id = self.request.matchdict['scheme_id']
        c_id = self.request.matchdict['c_id']
        print('concept_view ' + scheme_id + ' ' + c_id)
        prov = self.request.skos_registry.get_provider(scheme_id)
        if prov:
            c = prov.get_by_id(c_id)
            if c:
                skostype = ""
                if isinstance(c, Concept):
                    skostype = "Concept"
                if isinstance(c, Collection):
                    skostype = "Collection"
                return {'concept': c, 'conceptType': skostype}
        return {'concept': None}