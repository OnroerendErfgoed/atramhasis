from dogpile.cache import make_region

tree_region = make_region()
tree_cache_dictionary = {}

list_region = make_region()
list_cache_dictionary = {}


def includeme(config):

    if not tree_region.is_configured:
        # tree_region.configure_from_config(kw, 'cache.') # https://github.com/OnroerendErfgoed/oeauth/blob/master/oeauth/oauth.py#L126
        tree_region.configure(
            'dogpile.cache.memory',
            arguments={
                "cache_dict": tree_cache_dictionary
            }
        )
    if not list_region.is_configured:
        list_region.configure(
            'dogpile.cache.memory',
            arguments={
                "cache_dict": list_cache_dictionary
            }
        )


def invalidate_scheme_cache(conceptscheme_id):
    keys = tree_cache_dictionary.keys()
    keys_to_delete = [k for k in keys if k.split("|")[1].split()[0] == conceptscheme_id]
    tree_region.delete_multi(keys_to_delete)


def invalidate_cache():
    keys = tree_cache_dictionary.keys()
    keys_to_delete = [key for key in keys]
    tree_region.delete_multi(keys_to_delete)
