# -*- coding: utf-8 -*-

"""Application bootstrapping.

This file should not import anything else in the application in order to
prevent cyclic imports.

The `BASE_CONFIG` dict is loaded **before** the configuration file and should
contain default values for required parameters.

The `FORCED_CONFIG` dict is loaded **after** the configuration file and should
contain any parameter value that should not be changed by the user in their
own configuration file.
"""

from flask_babel import lazy_gettext as _l


# Available locales
LANGUAGES = ['en', 'es']
LANGUAGES_LOCALIZED = [_l('English'), _l('Spanish')]


# Default configuration values
BASE_CONFIG = {
    # General settings
    'SITENAME': 'My App',
    'ITEMS_PER_PAGE': 10,
    'LANGUAGES': LANGUAGES,

    # Uploads
    'MAX_CONTENT_LENGTH': 4 * 1024 * 1024, # 4 MB

    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,

    # Hashids
    'USER_HASHID_LENGTH': 10,
    'USER_HASHID_SALT': 'salty',

    # Localization
    'BABEL_DEFAULT_LOCALE': 'en',
    'BABEL_DEFAULT_TIMEZONE': 'UTC',

    # Crypto
    'PASSLIB_SCHEMES': ['bcrypt'],
    'PASSLIB_DEPRECATED': ['auto'],
    'PASSLIB_ALG_BCRYPT_ROUNDS': 14,
}


# Forced configuration values
FORCED_CONFIG = {
    'EXAMPLE': 'value'
}
