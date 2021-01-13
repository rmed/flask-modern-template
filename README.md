# Flask application template

This is a [Flask](https://github.com/pallets/flask) application template, including:

- Basic authentication through [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- Cryptography management through [passlib](https://pypi.org/project/passlib/)
- [Hashids](https://hashids.org/) support (see the `hashids_hasher` object in `app/__init__.py`
- Localization support per user, including timezones, through [Flask-Babel](https://github.com/python-babel/flask-babel)
- Database migrations ([Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/))
- CSRF protection for AJAX calls
- Markdown support ([Flask-Misaka](https://flask-misaka.readthedocs.io/en/latest/))
- Datetime filter for Jinja templates (see `format_datetime` function)
- Asset management through [Flask-Assets](https://flask-assets.readthedocs.io/en/latest/) and external assets through [Yarn](https://yarnpkg.com/)
- Default basic and development configurations (see `development.cfg` and `app/bootstrap.py`)
- Default layout using [Bulma](https://bulma.io)
- Custom macros (**render form fields**, **render pagination controls**, etc.)
- CLI commands (user management, translation)
- Optional asynchronous tasks through [Celery](https://pypi.org/project/celery/)
- A default `setup.py` file

## Getting started

1. Clone the repository
2. Modify the package name (remember to also modify `setup.py`, `babel.cfg`, `MANIFEST.in` and `translation.py` to reflect the new directory!)
3. Install the package in editable mode (virtual environment recommended):

```shell
$ pip install -e .
```

4. Adjust `app/models.py` to add or remove fields to the database
5. Create the first database migration for the development environment (set the `APP_CONFIG` environment variable and note that the command may have changed in `setup.py`):

```shell
$ myapp db init
$ myapp db migrate
```

6. Adjust the database migration file and execute it:

```shell
$ myapp db upgrade
```

**Note:** In the development environment it will be necessary to also install the *extras* defined in `setup.py`.

## Localization

A `translation.py` script is included to act as shortcut for `pybabel`. It defines the following commands:

- `translate.py compile`: compiles all localization files
- `translate.py init <lang>`: initializes a new translation with the given `<lang>` code
- `translate.py update`: updates all message catalogues with strings extracted from the application directory

This script uses the `babel.cfg` configuration file to specify how strings should be extracted from the project.

## Assets

External assets are managed through Yarn. In order to install them:

```shell
$ cd app/static 
$ yarn
```

This will download everything into `app/static/node_modules`.

Internal **asset bundles** are defined in the `init_app()` function inside `app/__init__.py`. By default, webassets is configured to use `libsass` and `rcssmin` for compilation and minification of SCSS files and `rjsmin` for minification of Javascript files. These assets are *compiled* into the `app/static/dist` directory **automatically in development environments**, but can be manually generated (e.g. prior to distribution) as well:

```shell
$ myapp assets build
```

Note that when distributing the application (either as a source distribution or a binary distribution) only the `app/static/dist` directory will be included. This means that any source file (e.g. `node_modules`) will be ignored.

## CSRF

By default, all AJAX requests that could modify data (`POST`, `PUT`, etc.) are protected with a CSRF token when the document is loaded. This token is conditionally included in the default layout as follows:

```html+jinja
{# CSRF token. Set flag in templates when needed #}
{% if _include_csrf %}
    <meta name="csrf-token" content="{{ csrf_token() }}"/>
{% endif %}
```

In order to enable the token, simply extend the layout in a template and set the value of `_include_csrf`:

```html+jinja
{% extends "layout.html" %}

{% set _include_csrf = true %}

{% block content %}
    Content here....
{% endblock %}
```

## Configuration

The configuration file is loaded on startup from the path defined in the `APP_CONFIG` environment variable. However, the `app/bootstrap.py` file contains base and default configuration values in the following dict structures:

- `BASE_CONFIG` dict is loaded **before** the configuration file and should contain default values for required parameters
- `FORCED_CONFIG` dict is loaded **after** the configuration file and should contain any parameter value that should not be changed by the user in their own configuration file

Therefore, configuration is loaded in the following way:

```text
bootstrap.BASE_CONFIG -> config file -> bootstrap.FORCED_CONFIG
```

The `development.cfg` file is a Python file in which parameters may be set using a `key = value` approach. Any **Flask extension configuration parameter** can be set here (usually in uppercase) and it will be loaded into the application. This file contains comments for every parameter defined in it and can be used as a base for **production configurations**.
