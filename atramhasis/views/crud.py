# -*- coding: utf-8 -*-
"""
Module containing views related to the REST service.
"""

import colander
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPMethodNotAllowed
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy.orm.exc import NoResultFound
from skosprovider_sqlalchemy.models import Concept, Collection

from atramhasis.errors import SkosRegistryNotFoundException, ConceptSchemeNotFoundException, \
    ValidationError, ConceptNotFoundException
from atramhasis.mappers import map_concept, map_conceptscheme
from atramhasis.protected_resources import protected_operation
from atramhasis.utils import from_thing, internal_providers_only
from atramhasis.cache import invalidate_scheme_cache
from atramhasis.audit import audit
from pyramid_skosprovider.views import ProviderView


@view_defaults(accept='application/json', renderer='skosrenderer_verbose')
class AtramhasisCrud(object):
    """
    This object groups CRUD REST views part of the private user interface.
    """

    def __init__(self, context, request):
        self.request = request
        self.skos_manager = self.request.data_managers['skos_manager']
        self.conceptscheme_manager = self.request.data_managers['conceptscheme_manager']
        self.context = context
        self.logged_in = request.authenticated_userid
        if 'scheme_id' in self.request.matchdict:
            self.scheme_id = self.request.matchdict['scheme_id']
            if hasattr(request, 'skos_registry') and request.skos_registry is not None:
                self.skos_registry = self.request.skos_registry
            else:
                raise SkosRegistryNotFoundException()
            self.provider = self.skos_registry.get_provider(self.scheme_id)
            if not self.provider:
                raise ConceptSchemeNotFoundException(self.scheme_id)

    def _get_json_body(self):
        json_body = self.request.json_body
        if 'c_id' in self.request.matchdict and 'id' not in json_body:
            json_body['id'] = self.request.matchdict['c_id']
        return json_body

    def _validate_concept(self, json_concept, conceptscheme_id):
        from atramhasis.validators import (
            Concept as ConceptSchema,
            concept_schema_validator
        )

        concept_schema = ConceptSchema(
            validator=concept_schema_validator
        ).bind(
            request=self.request,
            conceptscheme_id=conceptscheme_id
        )
        try:
            return concept_schema.deserialize(json_concept)
        except colander.Invalid as e:
            raise ValidationError(
                'Concept could not be validated',
                e.asdict()
            )

    def _validate_conceptscheme(self, json_conceptscheme):
        from atramhasis.validators import (
            ConceptScheme as ConceptSchemeSchema,
            conceptscheme_schema_validator
        )

        conceptscheme_schema = ConceptSchemeSchema(
            validator=conceptscheme_schema_validator
        ).bind(
            request=self.request
        )
        try:
            return conceptscheme_schema.deserialize(json_conceptscheme)
        except colander.Invalid as e:  # pragma no cover
            # I doubt this code will ever be reached, keeping it here just in case
            raise ValidationError(
                'Conceptscheme could not be validated',
                e.asdict()
            )

    @audit
    @view_config(route_name='atramhasis.get_conceptscheme', permission='view')
    def get_conceptscheme(self):
        if self.request.method == 'DELETE':
            raise HTTPMethodNotAllowed
        # is the same as the pyramid_skosprovider get_conceptscheme function, but wrapped with the audit function
        return ProviderView(self.request).get_conceptscheme()

    @view_config(route_name='atramhasis.edit_conceptscheme', permission='edit')
    def edit_conceptscheme(self):
        """
        Edit an existing concept

        :raises atramhasis.errors.ValidationError: If the provided json can't be validated
        """
        validated_json_conceptscheme = self._validate_conceptscheme(self._get_json_body())
        conceptscheme = self.conceptscheme_manager.get(self.provider.conceptscheme_id)
        conceptscheme = map_conceptscheme(conceptscheme, validated_json_conceptscheme)
        conceptscheme = self.conceptscheme_manager.save(conceptscheme)
        self.request.response.status = '200'
        return conceptscheme

    @view_config(route_name='atramhasis.get_conceptschemes', permission='view')
    def get_conceptschemes(self):
        if self.request.method == 'POST':
            raise HTTPMethodNotAllowed
        # is the same as the pyramid_skosprovider get_conceptscheme function, method not allowed included
        from pyramid_skosprovider.views import ProviderView
        return ProviderView(self.request).get_conceptschemes()

    @audit
    @view_config(route_name='atramhasis.get_concept', permission='view')
    def get_concept(self):
        """
        Get an existing concept

        :raises atramhasis.errors.ConceptNotFoundException: If the concept can't be found
        """
        c_id = self.request.matchdict['c_id']
        if isinstance(self.provider, SQLAlchemyProvider):
            try:
                concept = self.skos_manager.get_thing(c_id, self.provider.conceptscheme_id)
            except NoResultFound:
                raise ConceptNotFoundException(c_id)
        else:
            concept = self.provider.get_by_id(c_id)
            if not concept:
                raise ConceptNotFoundException(c_id)

        self.request.response.status = '200'
        return concept

    @internal_providers_only
    @view_config(route_name='atramhasis.add_concept', permission='edit')
    def add_concept(self):
        """
        Add a new concept to a conceptscheme

        :raises atramhasis.errors.ValidationError: If the provided json can't be validated
        """
        validated_json_concept = self._validate_concept(self._get_json_body(), self.provider.conceptscheme_id)
        cid = self.skos_manager.get_next_cid(self.provider.conceptscheme_id)
        if not cid:
            cid = 0
        cid += 1
        if validated_json_concept['type'] == 'concept':
            concept = Concept()
        else:
            concept = Collection()
        concept.concept_id = cid
        concept.conceptscheme_id = self.provider.conceptscheme_id
        concept.uri = self.provider.uri_generator.generate(id=concept.concept_id)
        map_concept(concept, validated_json_concept, self.skos_manager)
        concept = self.skos_manager.save(concept)

        invalidate_scheme_cache(self.scheme_id)

        self.request.response.status = '201'
        self.request.response.location = self.request.route_path(
            'skosprovider.c', scheme_id=self.scheme_id, c_id=concept.concept_id)
        return from_thing(concept)

    @internal_providers_only
    @view_config(route_name='atramhasis.edit_concept', permission='edit')
    def edit_concept(self):
        """
        Edit an existing concept

        :raises atramhasis.errors.ConceptNotFoundException: If the concept can't be found
        :raises atramhasis.errors.ValidationError: If the provided json can't be validated
        """
        c_id = self.request.matchdict['c_id']
        validated_json_concept = self._validate_concept(self._get_json_body(), self.provider.conceptscheme_id)
        try:
            concept = self.skos_manager.get_thing(c_id, self.provider.conceptscheme_id)
        except NoResultFound:
            raise ConceptNotFoundException(c_id)
        map_concept(concept, validated_json_concept, self.skos_manager)

        invalidate_scheme_cache(self.scheme_id)

        self.request.response.status = '200'
        return from_thing(concept)

    @internal_providers_only
    @protected_operation
    @view_config(route_name='atramhasis.delete_concept', permission='delete')
    def delete_concept(self):
        """
        Delete an existing concept

        :raises atramhasis.errors.ConceptNotFoundException: If the concept can't be found
        """
        c_id = self.request.matchdict['c_id']
        try:
            concept = self.skos_manager.get_thing(c_id, self.provider.conceptscheme_id)
        except NoResultFound:
            raise ConceptNotFoundException(c_id)
        self.skos_manager.delete_thing(concept)

        invalidate_scheme_cache(self.scheme_id)

        self.request.response.status = '200'
        return from_thing(concept)
