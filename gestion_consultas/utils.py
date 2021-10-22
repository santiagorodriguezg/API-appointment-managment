"""Project utilities"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Value
from django.db.models.functions import Concat
from django.template.loader import render_to_string
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


def filter_by_full_name(queryset, first_name_field, last_name_field, value):
    """
    Filter by user's full name

    :param queryset: QuerySet
    :param first_name_field: Field indicating the user's first name
    :param last_name_field: Field indicating the user's last name
    :param value: Value to be searched
    """
    return (queryset.annotate(full_name=Concat(first_name_field, Value(' '), last_name_field)).
            filter(full_name__unaccent__icontains=value))


def send_email(recipient_email, template_prefix, template_context):
    """Send reset password link to given user."""
    subject = render_to_string(f'{template_prefix}_subject.txt', template_context)
    subject = " ".join(subject.splitlines()).strip()  # Remove superfluous line breaks
    content = render_to_string(f'{template_prefix}.html', template_context)
    msg = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [recipient_email])
    msg.attach_alternative(content, "text/html")
    return msg.send()
