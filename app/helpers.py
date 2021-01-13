# -*- coding: utf-8 -*-

"""Application helpers."""

from hashids import Hashids
from passlib.context import CryptContext


class CeleryWrapper(object):
    """Wrapper for deferred initialization of Celery."""

    def __init__(self):
        self._celery = None
        self.task = None

    def __getattr__(self, attr: str):
        """Wrap internal celery attributes."""
        if attr == 'init_app':
            return getattr(self, attr)

        return getattr(self._celery, attr)

    def init_app(self, app):
        """Create a celery instance for the application.

        Args:
            app: Application instance
        """
        if not app.config.get('USE_CELERY', False):
            app.logger.warning('Skipping Celery initialization')
            return

        # Celery is optional, import it here rather than globally
        from celery import Celery

        celery_instance = Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER']
        )

        celery_instance.conf.update(app.config)
        TaskBase = celery_instance.Task

        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery_instance.Task = ContextTask

        self._celery = celery_instance
        self.task = self._celery.task


class CryptoManager(object):
    """Wrapper for passlib cryptography.

    The manager expects the following configuration variables:

    - `PASSLIB_SCHEMES`: List of passlib hashes for the underlying
        `CryptoContext` object. If a string is provided, it should be a
        comma-separated list of hashes supported by `passlib`. Defaults to
        `'bcrypt'`.
    - `PASSLIB_DEPRECATED`: List of passlib hashes that are deprecated
        (defaults to `"auto"`, which will deprecate all hashes except
        for the first hash type present in the `PASSLIB_SCHEMES` configuration
        variable). If a string different from `"auto"` is provided, it should
        be a comma-separated list of hashes supported by `passlib`. Defaults
        to an empty list.

    Moreover, the manager offers a direct translation of optional algorithm options for
    the underlying context (see
    <https://passlib.readthedocs.io/en/stable/lib/passlib.context.html#algorithm-options>).
    These are in the form `PASSLIB_ALG_<SCHEME>_<CONFIG>` and will be translated to the
    appropriate `<scheme>__<config>` configuration variable name internally.
    """

    def __init__(self):
        self._context = None

    def __getattr__(self, attr):
        """Wrap the internal passlib context."""
        if attr in ('init_app', '_context'):
            return getattr(self, attr)

        # Calling hasher methods
        return getattr(self._context, attr)

    def init_app(self, app):
        """Initialize manager.

        Args:
            app: Application instance

        Raises:
            `ModuleNotFoundError` in case `passlib` is not installed or
            `KeyError` if a configuration variable is missing.
        """
        schemes = app.config.get('PASSLIB_SCHEMES', 'bcrypt')
        deprecated = app.config.get('PASSLIB_DEPRECATED', 'auto')

        if isinstance(schemes, str):
            schemes = [s.strip() for s in schemes.split(',')]

        if isinstance(deprecated, str):
            deprecated = [d.strip() for d in deprecated.split(',')]

        params = {
            'schemes': schemes,
            'deprecated': deprecated,
        }

        # Set algorithm options
        for key in [k for k in app.config if k.startswith('PASSLIB_ALG_')]:
            value = app.config[key]
            scheme, option = key.replace('PASSLIB_ALG_', '').lower().split('_', 1)

            params['{}__{}'.format(scheme, option)] = value

        self._context = CryptContext(**params)


class HashidsWrapper(object):
    """Wrapper for deferred initialization of Hashids."""

    def __init__(self, salt: str = 'myapp', length: int = 8):
        self._hasher = None

    def __getattr__(self, attr: str):
        """Wrap internal Hashids attributes."""
        if attr == 'init_app':
            return getattr(self, attr)

        return getattr(self._hasher, attr)

    def init_app(self, salt: str = 'myapp', length: int = 8):
        """Initialize a hasher.

        Args:
            salt (str): Salt for the hash.
            length (int): Minimum length the generated hashes will have.
        """
        self._hasher = Hashids(salt=salt, min_length=length)
