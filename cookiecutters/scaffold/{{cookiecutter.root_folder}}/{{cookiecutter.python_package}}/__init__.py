from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application."""
    with Configurator(settings=settings) as config:
        config.include('atramhasis')
        # Set up atramhasis db
        config.include('atramhasis:data.db')

        return config.make_wsgi_app()
