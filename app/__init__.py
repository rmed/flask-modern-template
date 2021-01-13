# -*- coding: utf-8 -*-

"""Initialization code."""

import os

from logging.config import dictConfig

from flask import Flask
from flask_assets import Environment, Bundle
from flask_babel import Babel, _
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

import webassets

from .bootstrap import BASE_CONFIG, FORCED_CONFIG
from .errors import forbidden_403, not_found_404, server_error_500
from .helpers import CeleryWrapper, CryptoManager, HashidsWrapper

__version__ = '1.0.0'

# Logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Debug toolbar (for development)
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension()

    _USING_TOOLBAR = True

except ImportError:
    _USING_TOOLBAR = False


# Crypto
crypto_manager = CryptoManager()

# Hashids
user_hasher = HashidsWrapper()

# Babel
babel = Babel()

# CSRF
csrf = CSRFProtect()

# SQLAlchemy
db = SQLAlchemy()

# Flask-Migrate
migrate = Migrate()

# Flask-Mail
mail = Mail()

# Flask-Login
login_manager = LoginManager()

# Celery (optional)
celery = CeleryWrapper()

# Flask-Assets
assets = Environment()

# Flask-Misaka
md = Misaka(
    fenced_code=False,
    underline=True,
    no_intra_emphasis=False,
    strikethrough=True,
    superscript=True,
    tables=True,
    no_html=True,
    escape=True
)

# Utilities
from . import util


def init_app() -> Flask:
    """Initialize Shouko."""
    app = Flask(__name__)
    app.config.update(BASE_CONFIG)

    # Load configuration specified in environment variable or default
    # development one.
    # Production configurations shold be stored in a separate directory, such
    # as `instance`.
    if 'APP_CONFIG' in os.environ:
        app.config.from_envvar('APP_CONFIG')

    else:
        print((
            'WARNING: no configuration specified in APP_CONFIG, '
            'using default values!'
        ))

    app.config.update(FORCED_CONFIG)

    # Misc configurations
    app.config['ASSETS_AUTO_BUILD'] = False if app.config['ENV'] == 'production' else True
    app.config['__version__'] = __version__

    # Custom jinja helpers
    app.jinja_env.filters['datetime'] = util.format_datetime
    app.jinja_env.globals['url_for_self'] = util.url_for_self

    # Whitespacing Jinja
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Setup debug toolbar in development
    if app.config.get('DEBUG') and _USING_TOOLBAR:
        toolbar.init_app(app)

    # Setup cryptography (passlib)
    crypto_manager.init_app(app)

    # Setup Hashids
    user_hasher.init_app(
        salt=app.config['USER_HASHID_SALT'],
        length=app.config['USER_HASHID_LENGTH']
    )

    # Setup localization
    babel.init_app(app)

    # Setup CSRF protection
    csrf.init_app(app)

    # Setup database
    db.init_app(app)
    # Force model registration
    from . import models

    # Database migrations
    migrations_dir = os.path.join(app.root_path, 'migrations')
    migrate.init_app(app, db, migrations_dir)

    # Setup Flask-Mail
    mail.init_app(app)

    # Celery support (optional)
    if app.config.get('USE_CELERY', False):
        celery.init_app(app)

        # Import tasks
        from .async_tasks import async_mail

    # Setup Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = _('Please login to continue')
    login_manager.login_message_category = 'info'
    login_manager.refresh_view = 'auth.reauthenticate'
    login_manager.needs_refresh_message = (
        _('To protect your account, please reauthenticate to access this page')
    )
    login_manager.needs_refresh_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user.

        Note that this also checks whether the user is active or not.

        Args:
            user_id (str): User ID in format 'ID_serial'.

        Returns:
            User instance or None if not found.
        """
        uid, serial = user_id.split('_', 1)

        user = (
            models.User.query
            .filter_by(id=uid)
            .filter_by(serial=serial)
            .filter_by(is_active=True)
        ).first()

        return user

    # Setup Flask-Assets and bundles
    assets.init_app(app)

    libsass = webassets.filter.get_filter('libsass', style='compressed')
    css_bundle = Bundle(
        Bundle('app.scss', filters=libsass),
        filters='rcssmin',
        output='dist/app.css'
    )

    js_bundle = Bundle(
        'node_modules/jquery/dist/jquery.min.js',
        Bundle(
            'node_modules/@fortawesome/fontawesome-free/js/fontawesome.min.js',
            'node_modules/@fortawesome/fontawesome-free/js/solid.min.js',
            'node_modules/noty/lib/noty.min.js',
            filters='rjsmin'
        ),
        # Import in order of dependency, init.js should be the last
        Bundle(
            'js/util.js',
            'js/navigation.js',
            'js/init.js',
            filters='rjsmin'
        ),
        output='dist/app.js'
    )

    assets.register('css_pack', css_bundle)
    assets.register('js_pack', js_bundle)

    # Setup Flask-Misaka
    md.init_app(app)

    # Register blueprints
    from .views.auth import bp_auth
    from .views.general import bp_general

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_general)

    # Custom commands
    from . import cli

    # Custom error handlers
    app.register_error_handler(403, forbidden_403)
    app.register_error_handler(404, not_found_404)
    app.register_error_handler(500, server_error_500)


    return app
