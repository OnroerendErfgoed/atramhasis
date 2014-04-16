from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/atramhasis.jinja2')
def my_view(request):
    test = 'test 1 2 3'
    return {'test': test, 'project': 'atramhasis'}

@view_config(route_name='foundation', renderer='templates/foundation.jinja2')
def my_view2(request):
    return {'project': 'atramhasis'}
