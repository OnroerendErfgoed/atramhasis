import os

from pyramid.response import Response
from pyramid.response import FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_registry
from skosprovider.skos import Concept
from skosprovider.skos import Collection
from sqlalchemy.orm.exc import NoResultFound
from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException
from skosprovider_sqlalchemy.models import Collection as DomainCollection
from skosprovider_sqlalchemy.models import Concept as DomainConcept
from dogpile.cache import make_region


@view_defaults(accept='text/html')
class AtramhasisView(object):
    '''
    This object groups HTML views part of the public user interface.
    '''

    region = make_region().configure(
        'dogpile.cache.memory'
    )

    def __init__(self, request):
        self.request = request
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()

    def _read_request_param(self, param):
        value = None
        if param in self.request.params:
            value = self.request.params.getone(param).strip()
            if not value:
                value = None    # pragma: no cover
        return value

    @view_config(name='favicon.ico')
    def favicon_view(self):
        '''
        This view returns the favicon when requested from the web root.

        :param request: A :class:`pyramid.request.Request`
        '''
        here = os.path.dirname(__file__)
        icon = os.path.join(os.path.dirname(here), 'static', 'img', 'favicon.ico')
        response = FileResponse(
            icon,
            request=self.request,
            content_type='image/x-icon'
        )
        return response

    @view_config(route_name='home', renderer='atramhasis:templates/atramhasis.jinja2')
    def home_view(self):
        '''
        This view displays the homepage.

        :param request: A :class:`pyramid.request.Request`
        '''
        conceptschemes = [x.get_metadata() for x in self.skos_registry.get_providers()]
        return {'conceptschemes': conceptschemes}

    @view_config(route_name='concept', renderer='atramhasis:templates/concept.jinja2')
    def concept_view(self):
        '''
        This view displays the concept details

        :param request: A :class:`pyramid.request.Request`
        '''
        scheme_id = self.request.matchdict['scheme_id']
        c_id = self.request.matchdict['c_id']
        prov = self.request.skos_registry.get_provider(scheme_id)
        if prov:
            c = prov.get_by_id(c_id)
            if c:
                skostype = ""
                if isinstance(c, Concept):
                    skostype = "Concept"
                if isinstance(c, Collection):
                    skostype = "Collection"
                return {'concept': c, 'conceptType': skostype, 'scheme_id': scheme_id}
        return Response(content_type='text/plain', status_int=404)

    @view_config(route_name='search_result', renderer='atramhasis:templates/search_result.jinja2')
    def search_result(self):
        '''
        This view displays the search results

        :param request: A :class:`pyramid.request.Request`
        '''
        scheme_id = self.request.matchdict['scheme_id']
        label = self._read_request_param('label')
        ctype = self._read_request_param('ctype')
        provider = self.skos_registry.get_provider(scheme_id)
        if provider:
            if label is not None:
                concepts = provider.find({'label': label, 'type': ctype}, language=self.request.locale_name)
            elif (label is None) and (ctype is not None):
                concepts = provider.find({'type': ctype}, language=self.request.locale_name)
            else:
                concepts = provider.get_all(language=self.request.locale_name)
            return {'concepts': concepts, 'scheme_id': scheme_id}
        return Response(content_type='text/plain', status_int=404)

    @view_config(route_name='locale')
    def set_locale_cookie(self):
        '''
        This view will set a language cookie

        :param request: A :class:`pyramid.request.Request`
        '''
        settings = get_current_registry().settings
        default_lang = settings.get('pyramid.default_locale_name')
        available_languages = settings.get('available_languages', default_lang).split()
        [x.lower() for x in available_languages]
        language = self.request.GET.get('language', default_lang).lower()
        if language not in available_languages:
            language = default_lang

        referer = self.request.referer
        if referer is not None:
            response = HTTPFound(location=referer)
        else:
            response = HTTPFound(location=self.request.route_url('home'))

        response.set_cookie('_LOCALE_',
                            value=language,
                            max_age=31536000)  # max_age = year
        return response

    @view_config(route_name='search_result_export', renderer='csv')
    def results_csv(self):
        header = ['conceptscheme', 'id', 'uri', 'type', 'label', 'prefLabels', 'altLabels', 'definition', 'broader', 'narrower', 'related']
        rows = []
        scheme_id = self.request.matchdict['scheme_id']
        label = self._read_request_param('label')
        ctype = self._read_request_param('ctype')
        provider = self.skos_registry.get_provider(scheme_id)
        if provider:
            if label is not None:
                concepts = provider.find({'label': label, 'type': ctype}, language=self.request.locale_name)
            elif (label is None) and (ctype is not None):
                concepts = provider.find({'type': ctype}, language=self.request.locale_name)
            else:
                concepts = provider.get_all(language=self.request.locale_name)
            for concept in concepts:
                rows.append((scheme_id, concept['id'], '<uri>', '<type>', concept['label'], '<prefLabels>', '<altLabels>', '<definition>', '<broader>', '<narrower>', '<related>'))
        return {
            'header': header,
            'rows': rows,
            'filename': 'atramhasis_export'
        }

    @view_config(route_name='scheme_tree', renderer='json', accept='application/json')
    def results_tree_json(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        locale = self.request.locale_name

        if provider:
            conceptscheme_id = provider.conceptscheme_id
            skostree = self.get_scheme(conceptscheme_id, locale)
            dicts = []
            for index, thing in enumerate(skostree, 1):
                dicts.append(self.parse_thing(thing, index, 'root'))

            return dicts
        return Response(status_int=404)

    @region.cache_on_arguments()
    def get_scheme(self, scheme_id, locale):
        tco = self.request.db\
            .query(DomainConcept)\
            .filter(
                DomainConcept.conceptscheme_id == scheme_id,
                ~DomainConcept.broader_concepts.any(),
                ~DomainCollection.member_of.any()
            ).all()
        tcl = self.request.db\
            .query(DomainCollection)\
            .filter(
                DomainCollection.conceptscheme_id == scheme_id,
                ~DomainCollection.member_of.any()
            ).all()

        scheme_tree = sorted(tco, key=lambda child: child.label(locale).label.lower()) + \
            sorted(tcl, key=lambda child: child.label(locale).label.lower())

        return scheme_tree

    def parse_thing(self, thing, idx, parent):
        treeid = self.create_treeid(parent, idx)
        locale = self.request.locale_name

        if thing.type and thing.type == 'collection':
            cs = [member for member in thing.members] if hasattr(thing, 'members') else []
        else:
            cs = [c for c in thing.narrower_concepts]

        sortedcs = sorted(cs, key=lambda child: child.label(locale).label.lower())
        children = [self.parse_thing(c, index, treeid) for index, c in enumerate(sortedcs, 1)]
        dict_thing = {
            'id': treeid,
            'concept_id': thing.concept_id,
            'type': thing.type,
            'label': thing.label(locale).label,
            'children': children
        }

        return dict_thing

    def create_treeid(self, parentid, counter):
        if parentid == 'root':
            return str(counter)
        else:
            return parentid + "." + str(counter)

    @view_config(route_name='scheme_root', renderer='atramhasis:templates/concept.jinja2')
    def results_tree_html(self):
        scheme_id = self.request.matchdict['scheme_id']
        return {'concept': None, 'conceptType': None, 'scheme_id': scheme_id}

@view_defaults(accept='text/html')
class AtramhasisAdminView(object):
    '''
    This object groups HTML views part of the admin user interface.
    '''

    def __init__(self, request):
        self.request = request
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()

    @view_config(route_name='admin', renderer='atramhasis:templates/admin.jinja2')
    def admin_view(self):
        return {'admin': None}
