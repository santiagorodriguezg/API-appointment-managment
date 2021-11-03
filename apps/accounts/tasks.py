"""Accounts Celery tasks"""
from django.conf import settings
from django.core.management import call_command
from celery import shared_task

from apps.accounts.models import User
from gestion_consultas.utils import send_email


@shared_task
def delete_token_blacklist():
    """
    Delete any tokens from the outstanding list and blacklist that have expired.
    https://django-rest-framework-simplejwt.readthedocs.io/en/latest/blacklist_app.html#blacklist-app
    """
    call_command('flushexpiredtokens')
    print("djangorestframework-simplejwt command flushexpiredtokens completed")


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 2})
def send_email_to_user_created_by_admin(user_created_pk, raw_password):
    """Sends an email to the user created by the administrator"""
    user = User.objects.get(pk=user_created_pk)

    context = {
        'user': user,
        'password': raw_password,
        'login_url': f'{settings.CLIENT_DOMAIN}/accounts/login'
    }
    send_email(user.email, 'accounts/email/user_created_by_admin', context)
