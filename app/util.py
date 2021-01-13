# -*- coding: utf-8 -*-

"""Application utilities."""

import datetime

from typing import Optional
from urllib.parse import urlparse, urljoin

import pytz

from babel import dates as babel_dates
from flask import current_app, request, url_for
from flask_login import current_user
from flask_mail import Message

from . import babel, mail
from .bootstrap import LANGUAGES


# Localization
@babel.localeselector
def get_locale() -> Optional[str]:
    """Get locale from user or use default locale."""
    if not current_user or not current_user.is_authenticated:
        return request.accept_languages.best_match(LANGUAGES)

    return current_user.locale or current_app.config.get('BABEL_DEFAULT_LOCALE', 'en')


# Miscellaneous
def format_datetime(value: datetime.datetime) -> str:
    """Jinja filter to format datetime using user defined timezone.

    If a valid timezone is not set, will use application default.

    Args:
        value (datetime): Datetime object to represent.

    Returns:
        String representation of the datetime object.
    """
    user_tz = current_user.timezone

    if not user_tz or user_tz not in pytz.common_timezones:
        user_tz = current_app.config.get('BABEL_DEFAULT_TIMEZONE', 'UTC')

    tz = babel_dates.get_timezone(user_tz)

    return babel_dates.format_datetime(
        value,
        'yyyy-MM-dd HH:mm:ss',
        tzinfo=tz
    )


def is_ajax() -> bool:
    """Detect whether the request was made through AJAX.

    In order to detect this, the `X-WITH-AJAX` header should be set to
    "true".

    Returns:
        `True` if the request was made through AJAX, otherwise `False`.
    """
    return request.headers.get('X-WITH-AJAX', 'false') == 'true'


def is_safe_url(target: str) -> bool:
    """Check whether the target is safe for redirection.

    Args:
        target (str): Target URL/path.

    Returns:
        `True` if the URL is safe, otherwise `False`.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def send_email(*args, **kwargs):
    """Send an email.

    Emails are sent asynchronously if Celery is enabled.

    All arguments are passed as-is to Flask-Mail.

    Returns:
        Mail send result or `None`.
    """
    if current_app.config.get('USE_CELERY', False):
        from .async_tasks import async_mail

        async_mail.delay(*args, **kwargs)

    else:
        message = Message(*args, **kwargs)

        return mail.send(message)


def url_for_self(**kwargs) -> str:
    """Helper to return current endpoint in Jinja template."""
    return url_for(request.endpoint, **dict(request.view_args, **kwargs))
