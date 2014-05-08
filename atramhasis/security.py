import json

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPServerError
from pyramid.response import Response
from pyramid.security import Allow, ALL_PERMISSIONS, forget, remember
from pyramid.view import view_defaults, view_config
import requests


def groupfinder(userid, request):
    if userid:
        return ['g:edit']


class Root(object):
    __acl__ = [
        (Allow, 'g:edit', 'edit'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        print('__init__')
        print(request.authenticated_userid)
        print(groupfinder(request.authenticated_userid, request))
        self.request = request


@view_defaults()
class LoginView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='login')
    def login(self):
        print('-' * 35 + '> login')
        assertion = self.request.params.get('assertion')
        if not assertion:
            return HTTPBadRequest()
        data = {'assertion': assertion, 'audience': 'http://localhost:6543/'}
        resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)

        if resp.ok:
            verification_data = json.loads(resp.content.decode())

            # Check if the assertion was valid
            if verification_data['status'] == 'okay':
                email = verification_data['email']
                headers = remember(self.request, email, max_age='1000')
                response = Response(json={'email': email}, headers=headers, status_int=200)
                response.set_cookie('_USER_', value=email, max_age=1000)
                return response
        return HTTPServerError()

    @view_config(route_name='logout')
    def logout(self):
        print('-' * 35 + '> logout')
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url('home'),
                         headers=headers)