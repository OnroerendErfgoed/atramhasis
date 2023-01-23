import colander
from pyramid.view import view_config
from pyramid.view import view_defaults
from skosprovider_sqlalchemy.models import Language
from sqlalchemy.exc import NoResultFound

from atramhasis.errors import LanguageNotFoundException
from atramhasis.errors import ValidationError
from atramhasis.validators import LanguageTag
from atramhasis.validators import languagetag_validator


@view_defaults(accept='application/json', renderer='skosrenderer_verbose')
class LanguagesCrud:
    """
    This object groups CRUD REST views for languages.
    """

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.logged_in = request.authenticated_userid
        self.languages_manager = self.request.data_managers['languages_manager']

    def _get_json_body(self):
        json_body = self.request.json_body
        if 'l_id' in self.request.matchdict and 'id' not in json_body:
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
        """
        Get all existing languages

        :return: list of languages
        """
        if 'sort' in self.request.params:
            sort = self.request.params['sort']
            sort_desc = (sort[0:1] == '-')
            sort = sort[1:] if sort[0:1] in ['-', '+'] else sort
            sort = sort.strip()
            languages = self.languages_manager.get_all_sorted(sort, sort_desc)
        else:
            languages = self.languages_manager.get_all()
        return languages

    @view_config(route_name='atramhasis.get_language', permission='edit')
    def get_language(self):
        """
        Get an existing language

        :raises atramhasis.errors.LanguageNotFoundException: If the language can't be found
        :return the corresponding language
        """
        l_id = self.request.matchdict['l_id']
        try:
            language = self.languages_manager.get(l_id)
        except NoResultFound:
            raise LanguageNotFoundException(l_id)

        self.request.response.status = '200'
        return language

    @view_config(route_name='atramhasis.edit_language', permission='edit')
    def edit_language(self):
        """
        Edit an existing language or create when not found

        :raises atramhasis.errors.ValidationError: If the provided json can't be validated
        """
        l_id = self.request.matchdict['l_id']
        json_body = self._get_json_body()
        json_body['id'] = l_id

        try:
            language = self.languages_manager.get(l_id)
            validated_json_language = self._validate_language(json_body, False)
            language.name = validated_json_language['name']
        except NoResultFound:
            validated_json_language = self._validate_language(json_body, True)
            language = Language(id=validated_json_language['id'], name=validated_json_language['name'])
        language = self.languages_manager.save(language)
        self.request.response.status = '200'
        return {'id': language.id, 'name': language.name}

    @view_config(route_name='atramhasis.delete_language', permission='edit')
    def delete_language(self):
        """
        Delete an existing concept

        :raises atramhasis.errors.LanguageNotFoundException: If the language can't be found
        """
        l_id = self.request.matchdict['l_id']
        try:
            language = self.languages_manager.get(l_id)
        except NoResultFound:
            raise LanguageNotFoundException(l_id)
        self.languages_manager.delete(language)

        self.request.response.status = '200'
        return {'id': language.id, 'name': language.name}
