import os

from pyramid.response import Response
from pyramid.response import FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_registry
from pyramid.i18n import TranslationStringFactory
from sqlalchemy.orm.exc import NoResultFound
from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException, ConceptNotFoundException,\
    DbNotFoundException
from skosprovider_sqlalchemy.models import Collection, Thing, Concept, LabelType, NoteType
from atramhasis.service import AtramhasisService
from atramhasis.views import tree_region, invalidate_scheme_cache, invalidate_cache


def labels_to_string(labels, ltype):
    labelstring = ''
    for label in (l for l in labels if l.labeltype_id == ltype):
        labelstring += label.label + ' (' + label.language_id + '), '
    return labelstring[:-2]


def get_definition(notes):
    for note in notes:
        if note.notetype_id == 'definition':
            return note.note


@view_defaults(accept='text/html')
class AtramhasisView(object):
    '''
    This object groups HTML views part of the public user interface.
    '''

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
                value = None  # pragma: no cover
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
        provider = self.request.skos_registry.get_provider(scheme_id)

        if not provider:
            raise ConceptSchemeNotFoundException(scheme_id)
        try:
            c = self.request.db.query(Thing) \
                .filter_by(concept_id=c_id, conceptscheme_id=provider.conceptscheme_id) \
                .one()
            if isinstance(c, Concept):
                concept_type = "Concept"
            elif isinstance(c, Collection):
                concept_type = "Collection"
            else:
                return Response('Thing without type: ' + str(c_id), status_int=500)
            return {'concept': c, 'conceptType': concept_type, 'scheme_id': scheme_id}
        except NoResultFound:
            raise ConceptNotFoundException(c_id)


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
        header = ['conceptscheme', 'id', 'uri', 'type', 'label', 'prefLabels', 'altLabels', 'definition', 'broader',
                  'narrower', 'related']
        rows = []
        scheme_id = self.request.matchdict['scheme_id']
        label = self._read_request_param('label')
        ctype = self._read_request_param('ctype')
        provider = self.skos_registry.get_provider(scheme_id)
        service = AtramhasisService(self.request.db, provider.conceptscheme_id)
        if provider:
            if label is not None:
                concepts = service.find({'label': label, 'type': ctype}, language=self.request.locale_name)
            elif (label is None) and (ctype is not None):
                concepts = service.find({'type': ctype}, language=self.request.locale_name)
            else:
                concepts = service.get_all(language=self.request.locale_name)
            for concept in concepts:
                if concept.type == 'concept':
                    rows.append((
                        scheme_id, concept.concept_id, concept.uri, concept.type,
                        concept.label(self.request.locale_name).label,
                        labels_to_string(concept.labels, 'prefLabel'), labels_to_string(concept.labels, 'altLabel'),
                        get_definition(concept.notes), [c.concept_id for c in concept.broader_concepts],
                        [c.concept_id for c in concept.narrower_concepts],
                        [c.concept_id for c in concept.related_concepts]))
                else:
                    rows.append((
                        scheme_id, concept.concept_id, concept.uri, concept.type,
                        concept.label(self.request.locale_name).label,
                        labels_to_string(concept.labels, 'prefLabel'), labels_to_string(concept.labels, 'altLabel'),
                        get_definition(concept.notes), '', [c.concept_id for c in concept.members], ''))
        return {
            'header': header,
            'rows': rows,
            'filename': 'atramhasis_export'
        }

    @view_config(route_name='scheme_tree', renderer='json', accept='application/json')
    def results_tree_json(self):
        scheme_id = self.request.matchdict['scheme_id']
        locale = self.request.locale_name
        skostree = self.get_scheme(scheme_id, locale)
        dicts = []
        for thing in skostree:
            dicts.append(self.parse_thing(thing, None))
        if dicts:
            return dicts
        else:
            return Response(status_int=404)

    @tree_region.cache_on_arguments()
    def get_scheme(self, scheme, locale):
        scheme_tree = []
        provider = self.skos_registry.get_provider(scheme)
        if provider:
            conceptscheme_id = provider.conceptscheme_id

            tco = self.request.db \
                .query(Concept) \
                .filter(
                Concept.conceptscheme_id == conceptscheme_id,
                ~Concept.broader_concepts.any(),
                ~Collection.member_of.any()
            ).all()
            tcl = self.request.db \
                .query(Collection) \
                .filter(
                Collection.conceptscheme_id == conceptscheme_id,
                ~Collection.member_of.any()
            ).all()

            scheme_tree = sorted(tco, key=lambda child: child.label(locale).label.lower()) + \
                          sorted(tcl, key=lambda child: child.label(locale).label.lower())

        return scheme_tree

    def parse_thing(self, thing, parent_tree_id):
        tree_id = self.create_treeid(parent_tree_id, thing.concept_id)
        locale = self.request.locale_name

        if thing.type and thing.type == 'collection':
            cs = [member for member in thing.members] if hasattr(thing, 'members') else []
        else:
            cs = [c for c in thing.narrower_concepts]

        sortedcs = sorted(cs, key=lambda child: child.label(locale).label.lower())
        children = [self.parse_thing(c, tree_id) for index, c in enumerate(sortedcs, 1)]
        dict_thing = {
            'id': tree_id,
            'concept_id': thing.concept_id,
            'type': thing.type,
            'label': thing.label(locale).label,
            'children': children
        }

        return dict_thing

    def create_treeid(self, parent_tree_id, concept_id):
        if parent_tree_id is None:
            return str(concept_id)
        else:
            return parent_tree_id + "." + str(concept_id)


    @view_config(route_name='scheme_root', renderer='atramhasis:templates/concept.jinja2')
    def results_tree_html(self):
        scheme_id = self.request.matchdict['scheme_id']
        return {'concept': None, 'conceptType': None, 'scheme_id': scheme_id}


@view_defaults(accept='application/json', renderer='json')
class AtramhasisListView(object):
    '''
    This object groups list views part for the user interface.
    '''
    def __init__(self, request):
        self.request = request
        if hasattr(request, 'db') and request.db is not None:
            self.db = request.db
        else:
            raise DbNotFoundException()
        self.localizer = request.localizer
        self._ = TranslationStringFactory('atramhasis')

    @view_config(route_name='labeltypes')
    def labeltype_list_view(self):
        labeltypes = self.get_list(LabelType)
        return [{"key": labeltype.name, "label": self.localizer.translate(self._(labeltype.name))}
                for labeltype in labeltypes]

    @view_config(route_name='notetypes')
    def notetype_list_view(self):
        notetypes = self.get_list(NoteType)
        return [{"key": notetype.name, "label": self.localizer.translate(self._(notetype.name))}
                for notetype in notetypes]

    @tree_region.cache_on_arguments()
    def get_list(self, listtype):
        return self.db.query(listtype).all()


@view_defaults(accept='text/html')
class AtramhasisAdminView(object):
    '''
    This object groups HTML views part of the admin user interface.
    '''

    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()

    @view_config(route_name='admin', renderer='atramhasis:templates/tempadmin.jinja2', permission='edit')
    def admin_view(self):
        return {'admin': None}

    @view_config(route_name='scheme_tree_invalidate', renderer='json', accept='application/json', permission='edit')
    def invalidate_scheme_tree(self):
        scheme_id = self.request.matchdict['scheme_id']
        invalidate_scheme_cache(scheme_id)
        return Response(status_int=200)

    @view_config(route_name='tree_invalidate', renderer='json', accept='application/json', permission='edit')
    def invalidate_tree(self):
        invalidate_cache()
        return Response(status_int=200)
