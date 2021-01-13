"""Translation commands."""

import os
import click

# Replace with the name of the app package
PACKAGE = 'app'


@click.group()
def cli():
    """Translation and localization commands."""
    pass


@cli.command()
def compile():
    """Compile all languages."""
    compile_cmd = (
        'pybabel compile '
        f'-d {PACKAGE}/translations'
    )

    if os.system(compile_cmd):
        raise RuntimeError('compile command failed')


@cli.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    extract_cmd = (
        'pybabel extract '
        '-F babel.cfg '
        '-k "lazy_gettext _l" '
        f'-o {PACKAGE}/translations/messages.pot .'
    )

    init_cmd = (
        'pybabel init '
        f'-i {PACKAGE}/translations/messages.pot '
        f'-d {PACKAGE}/translations '
        f'-l {lang}'
    )

    if os.system(extract_cmd):
        raise RuntimeError('extract command failed')

    if os.system(init_cmd):
        raise RuntimeError('init command failed')


@cli.command()
def update():
    """Update message catalog."""
    extract_cmd = (
        'pybabel extract '
        '-F babel.cfg '
        '-k "lazy_gettext _l" '
        f'-o {PACKAGE}/translations/messages.pot .'
    )

    update_cmd = (
        'pybabel update '
        f'-i {PACKAGE}/translations/messages.pot '
        f'-d {PACKAGE}/translations'
    )


    if os.system(extract_cmd):
        raise RuntimeError('extract command failed')

    if os.system(update_cmd):
        raise RuntimeError('update command failed')


if __name__ == '__main__':
    cli()
