from pyramid.view import view_config
from pyramid.response import Response

err_msg = """
No SKOS registry found, please check your application setup
"""

@view_config(route_name='home', renderer='templates/atramhasis.jinja2')
def home_view(request):
    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        conceptschemes = [x.get_metadata() for x in request.skos_registry.get_providers()]
        return {'project': 'atramhasis', 'conceptschemes': conceptschemes}
    else:
        return Response(err_msg, content_type='text/plain', status_int=500)