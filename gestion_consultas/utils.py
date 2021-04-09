"""Project utilities"""

from django.utils.text import slugify
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


def generate_random_field(model_instance, field, field_value):
    """
    Generate the value of a field given an initial value.
    :param model_instance: Model Class
    :param field: Name of the field used to filter given in type String
    :param field_value: Initial value of the field
    :return: New field value
    """
    new_field_value = slugify(field_value)
    model_class = model_instance.__class__

    while model_class._default_manager.filter(**{field: new_field_value}).exists():
        object_pk = model_class._default_manager.latest('pk')
        object_pk = object_pk.pk + 1
        new_field_value = f'{new_field_value}-{object_pk}'
    return new_field_value
