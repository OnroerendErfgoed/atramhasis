import os

from pyramid.response import FileResponse
from pyramid.view import view_config


class StaticView:
    """
    Views voor aan de root gebonden static files.
    """

    def __init__(self, request):
        self.request = request
        self.here = os.path.dirname(__file__)

    @view_config(route_name='sitemap')
    def sitemaps(self):
        sitemaps = os.path.join(
            self.here, '..', 'static', '_sitemaps', 'sitemap_index.xml'
        )
        return FileResponse(
            sitemaps,
            request=self.request
        )
