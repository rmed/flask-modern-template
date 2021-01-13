# -*- coding: utf-8 -*-

"""Asynchronous Celery tasks.

The `celery` package must be installed and the backend must be enabled and
configured with the `USE_CELERY` and `CELERY_*` parameters, respectively.
"""

from flask_mail import Message

from . import celery, mail


# Important! Always name your tasks
@celery.task(name='myapp.async_tasks.async_mail', ignore_result=True)
def async_mail(*args, **kwargs):
    """Send Flask-Mail emails asynchronously."""
    message = Message(*args, **kwargs)
    mail.send(message)
