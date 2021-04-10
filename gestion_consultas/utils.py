"""Project utilities"""

from rest_framework.filters import SearchFilter

REGEX_LETTERS_ONLY = '^[a-zA-ZÁ-ÿ+ ?]*$'


class UnaccentedSearchFilter(SearchFilter):
    """Unaccented Search Filter"""
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '~': 'unaccent__icontains',
        '@': 'search',
        '$': 'iregex',
    }
