# -*- coding: utf-8 -*-
import colander
from pyramid.view import view_defaults, view_config
from skosprovider_sqlalchemy.models import Language
from sqlalchemy.orm.exc import NoResultFound
from atramhasis.errors import LanguageNotFoundException, ValidationError
from atramhasis.validators import LanguageTag, languagetag_validator


@view_defaults(accept='application/json', renderer='skosrenderer_verbose')
class LanguagesCrud(object):
    '''
    This object groups CRUD REST views for languages.
    '''

    def __init__(self, context, request):
        self.request = request
        self.db = request.db
        self.context = context
        self.logged_in = request.authenticated_userid

    def _get_json_body(self):
        json_body = self.request.json_body
        if 'l_id' in self.request.matchdict and not 'id' in json_body:
            json_body['id'] = self.request.matchdict['l_id']
        return json_body

    def _validate_language(self, json_language, new):
        language = LanguageTag(
            validator=languagetag_validator
        ).bind(
            request=self.request,
            new=new
        )
        try:
            return language.deserialize(json_language)
        except colander.Invalid as e:
            raise ValidationError(
                'Language could not be validated',
                e.asdict()
            )

    @view_config(route_name='atramhasis.list_languages', permission='edit')
    def list_languages(self):
        '''
        Get all existing languages

        :return: list of languages
        '''
        languages = self.db.query(Language).all()
        return languages

    @view_config(route_name='atramhasis.get_language', permission='edit')
    def get_language(self):
        '''
        Get an existing language

        :raises atramhasis.errors.LanguageNotFoundException: If the language can't be found
        :return the corresponding language
        '''
        l_id = self.request.matchdict['l_id']
        try:
            language = self.db.query(Language).filter_by(id=l_id).one()
        except NoResultFound:
            raise LanguageNotFoundException(l_id)

        self.request.response.status = '200'
        return language

    @view_config(route_name='atramhasis.add_language', permission='edit')
    def add_language(self):
        '''
        Add a new language

        :raises atramhasis.errors.ValidationError: If the provided json can't be validated
        '''
        validated_json_language = self._validate_language(self._get_json_body(), True)
        language = Language(id=validated_json_language['id'], name=validated_json_language['name'])
        self.db.add(language)
        self.db.flush()
        self.request.response.status = '201'
        self.request.response.location = self.request.route_path(
            'atramhasis.get_language',  l_id=language.id)
        return {'id': language.id, 'name': language.name}


    @view_config(route_name='atramhasis.edit_language', permission='edit')
    def edit_language(self):
        '''
        Edit an existing language

        :raises atramhasis.errors.LanguageNotFoundException: If the language can't be found
        :raises atramhasis.errors.ValidationError: If the provided json can't be validated
        '''
        l_id = self.request.matchdict['l_id']
        validated_json_language = self._validate_language(self._get_json_body(), False)
        try:
            language = self.db.query(Language).filter_by(id=l_id).one()
        except NoResultFound:
            raise LanguageNotFoundException(l_id)
        language.name = validated_json_language['name']

        self.request.response.status = '200'
        return {'id': language.id, 'name': language.name}

    @view_config(route_name='atramhasis.delete_language', permission='edit')
    def delete_language(self):
        '''
        Delete an existing concept

        :raises atramhasis.errors.ConceptNotFoundException: If the concept can't be found
        '''
        l_id = self.request.matchdict['l_id']
        try:
            language = self.db.query(Language).filter_by(id=l_id).one()
        except NoResultFound:
            raise LanguageNotFoundException(l_id)
        self.db.delete(language)

        self.request.response.status = '200'
        return {'id': language.id, 'name': language.name}