from dogpile.cache import make_region

popular_concepts_dict = {}
popular_concepts = make_region().configure(
    'dogpile.cache.memory',
    arguments={
        'cache_dict': {}
    }
)
