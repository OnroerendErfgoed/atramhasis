"""
Module containing views related to the REST service.
"""
import logging
import time

import colander
import transaction
from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.httpexceptions import HTTPNoContent
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid_skosprovider.views import ProviderView
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from atramhasis import utils
from atramhasis.audit import audit
from atramhasis.cache import invalidate_scheme_cache
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.errors import ConceptNotFoundException
from atramhasis.errors import ConceptSchemeNotFoundException
from atramhasis.errors import SkosRegistryNotFoundException
from atramhasis.errors import ValidationError
from atramhasis.json_processors import provider
from atramhasis.mappers import map_concept
from atramhasis.mappers import map_conceptscheme
from atramhasis.protected_resources import protected_operation
from atramhasis.utils import from_thing
from atramhasis.utils import internal_providers_only

LOG = logging.getLogger(__name__)


@view_defaults(accept='application/json', renderer='skosrenderer_verbose')
class AtramhasisCrud:
    """
    This object groups CRUD REST views part of the private user interface.
    """

    def __init__(self, request):
        self.request = request
        self.skos_manager = self.request.data_managers['skos_manager']
        self.conceptscheme_manager = self.request.data_managers['conceptscheme_manager']
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

    def _validate_concept(self, json_concept, provider, validate_id_generation):
        from atramhasis.validators import (
            Concept as ConceptSchema,
            concept_schema_validator
        )

        concept_schema = ConceptSchema(
            validator=concept_schema_validator
        ).bind(
            request=self.request,
            provider=provider,
            validate_id_generation=validate_id_generation
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
        validated_json_concept = self._validate_concept(
            self._get_json_body(), self.provider, validate_id_generation=True
        )
        exc = None
        id_generation_strategy = IDGenerationStrategy.NUMERIC
        for _ in range(5):
            try:
                if validated_json_concept['type'] == 'concept':
                    concept = Concept()
                else:
                    concept = Collection()

                id_generation_strategy = self.provider.metadata.get(
                    "atramhasis.id_generation_strategy", IDGenerationStrategy.NUMERIC
                )
                if id_generation_strategy == IDGenerationStrategy.MANUAL:
                    concept.concept_id = validated_json_concept["id"]
                else:
                    concept.concept_id = self.skos_manager.get_next_cid(
                        self.provider.conceptscheme_id, id_generation_strategy
                    )

                concept.conceptscheme_id = self.provider.conceptscheme_id
                concept.uri = self.provider.uri_generator.generate(id=concept.concept_id)
                map_concept(concept, validated_json_concept, self.skos_manager)
                concept = self.skos_manager.save(concept)
                break
            except IntegrityError as exc:
                if id_generation_strategy == IDGenerationStrategy.MANUAL:
                    # Technically the concept_id is not 100% guaranteed to be the cause
                    # of an IntegrityError, so log trace just in case.
                    LOG.exception("Integrity error")

                    concept_id = validated_json_concept["concept_id"]
                    raise ValidationError(
                        "Integrity error", [{"concept_id": f"{concept_id} already exists."}]
                    )
                # There is a small chance that another concept gets added at the same
                # time. There is nothing wrong with the request, so we try again.
                transaction.abort()
                time.sleep(0.05)
        else:
            raise Exception(
                f"Could not save new concept due to IntegrityErrors. {exc}"
            )

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
        validated_json_concept = self._validate_concept(
            self._get_json_body(), self.provider, validate_id_generation=False
        )
        try:
            concept = self.skos_manager.get_thing(c_id, self.provider.conceptscheme_id)
        except NoResultFound:
            raise ConceptNotFoundException(c_id)
        concept = map_concept(concept, validated_json_concept, self.skos_manager)

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
        result = from_thing(concept)
        self.skos_manager.delete_thing(concept)

        invalidate_scheme_cache(self.scheme_id)

        self.request.response.status = '200'
        return result

    @view_config(
        route_name='atramhasis.providers',
        permission='view',
        request_method='GET',
        openapi=True,
    )
    def get_providers(self):
        query_params = self.request.openapi_validated.parameters.query
        if 'subject' in query_params:
            filters = {'subject': query_params['subject']}
        else:
            filters = {}
        return self.request.skos_registry.get_providers(**filters)

    @view_config(
        route_name='atramhasis.provider',
        permission='view',
        request_method='GET',
        openapi=True
    )
    def get_provider(self):
        return self.request.skos_registry.get_provider(self.request.matchdict["id"])

    @view_config(
        route_name='atramhasis.providers',
        permission='add-provider',
        request_method='POST',
        openapi=True
    )
    def add_provider(self):
        db_provider = provider.create_provider(
            json_data=self.request.openapi_validated.body,
            session=self.request.db,
            skos_registry=self.request.skos_registry,
        )
        self.request.response.status_code = 201
        return utils.db_provider_to_skosprovider(db_provider)

    @view_config(
        route_name='atramhasis.provider',
        permission='edit-provider',
        request_method='PUT',
        openapi=True
    )
    def update_provider(self):
        try:
            db_provider = provider.update_provider(
                provider_id=self.request.matchdict["id"],
                json_data=self.request.openapi_validated.body,
                session=self.request.db,
            )
            return utils.db_provider_to_skosprovider(db_provider)
        except NoResultFound:
            db_provider = provider.create_provider(
                json_data=self.request.openapi_validated.body,
                session=self.request.db,
                skos_registry=self.request.skos_registry,
            )
            self.request.response.status_code = 201
            return utils.db_provider_to_skosprovider(db_provider)

    @view_config(
        route_name='atramhasis.provider',
        permission='delete-provider',
        request_method='DELETE',
        openapi=True
    )
    def delete_provider(self):
        provider.delete_provider(
            provider_id=self.request.matchdict["id"],
            session=self.request.db,
        )
        return HTTPNoContent()
