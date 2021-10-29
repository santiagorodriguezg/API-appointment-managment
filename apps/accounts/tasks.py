"""Accounts Celery tasks"""

from django.core.management import call_command
from celery import shared_task


@shared_task
def delete_token_blacklist():
    """
    Delete any tokens from the outstanding list and blacklist that have expired.
    https://django-rest-framework-simplejwt.readthedocs.io/en/latest/blacklist_app.html#blacklist-app
    """
    call_command('flushexpiredtokens')
    print("djangorestframework-simplejwt command flushexpiredtokens completed")
