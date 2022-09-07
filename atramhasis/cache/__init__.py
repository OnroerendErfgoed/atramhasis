from dogpile.cache import make_region

tree_region = make_region()
list_region = make_region()


def includeme(config):
    settings = config.registry.settings
    if not tree_region.is_configured:
        tree_region.configure_from_config(settings, 'cache.tree.')
    if not list_region.is_configured:
        list_region.configure_from_config(settings, 'cache.list.')


def invalidate_scheme_cache(conceptscheme_id):
    # TODO implement propper conceptscheme cache invalidation if this is ever possible
    tree_region.invalidate()


def invalidate_cache():
    tree_region.invalidate()
