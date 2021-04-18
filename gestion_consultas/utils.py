"""Project utilities"""

from rest_framework.exceptions import NotFound
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


def get_queryset_with_pk(detail, queryset, pk):
    """
    Obtain an object given an pk.

    :param detail: Message to be displayed if the object is not found.
    :param queryset: Queryset
    :param pk: Object pk
    :raises NotFound If the object is not found.
    :return: List of items.
    """
    if pk is not None:
        try:
            int(pk)
        except Exception:
            raise NotFound(detail=detail)
        queryset = queryset.filter(pk=pk).first()
        if queryset is None:
            raise NotFound(detail=detail)
        return queryset

    return queryset
