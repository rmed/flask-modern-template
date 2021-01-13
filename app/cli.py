# -*- coding: utf-8 -*-

"""CLI commands."""

import click
from flask.cli import FlaskGroup
from sqlalchemy import exc as dbexc

from . import db, crypto_manager, init_app
from .models import User


def init_wrapper(info):
    """Wrapper for the application initialization function."""
    return init_app()


@click.group(cls=FlaskGroup, create_app=init_wrapper)
def cli():
    """App CLI."""
    pass


# Begin user commands
@cli.group()
def user():
    """User management commands."""
    pass


@user.command('create')
@click.option('--username', help='username (must be unique)', prompt=True)
@click.option('--email', help='email (must be unique)', prompt=True)
@click.option('--password', help='password', prompt=True, hide_input=True)
def create_user(username: str, email: str, password: str):
    """Add a new user to the database."""
    hashed_password = crypto_manager.hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        is_active=True
    )

    try:
        correct = True
        db.session.add(new_user)
        db.session.commit()

        click.echo('New user created')

    except dbexc.IntegrityError as e:
        correct = False
        click.echo('A user with those details already exists. More information:')
        click.echo(e.orig)

    except Exception as e:
        correct = False
        click.echo('Error creating user:')
        click.echo(e)

    finally:
        if not correct:
            db.session.rollback()


@user.command('info')
@click.option('--username', help='username to search (priority over email)')
@click.option('--email', help='email to search')
def user_info(username: str, email: str):
    """Get user information from database."""
    if not username and not email:
        click.echo('You must provide either a username or an email')
        return

    user = None

    if username:
        user = User.get_by_username(username)

    else:
        user = User.get_by_email(email)

    if not user:
        click.echo('Could not find user')
        return

    click.echo('Username: {}'.format(user.username))
    click.echo('Email: {}'.format(user.email))
    click.echo('Active: {}'.format('yes' if user.is_active else 'no'))
    click.echo('Joined: {} UTC'.format(user.joined_at.strftime('%Y-%m-%d %H:%M:%S')))
    click.echo('Locale: {}'.format(user.locale))
    click.echo('Timezone: {}'.format(user.timezone))
    click.echo('Invitations remaining: {}'.format(user.invites))


@user.command('activate')
@click.argument('username')
def activate_user(username: str):
    """Activate a user account, effectively allowing them to login.

    \b
    Args:
        username: the username to enable
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    if user.is_active:
        click.echo('User is already active')
        return

    user.is_active = True

    try:
        correct = True
        db.session.commit()
        click.echo('Correctly activated user')

    except Exception as e:
        correct = False
        click.echo('Failed to activate user:')
        click.echo(e)

    finally:
        if not correct:
            db.session.rollback()


@user.command('deactivate')
@click.argument('username')
def deactivate_user(username: str):
    """Disable a user account, effectively forbidding them from logging in.

    \b
    Args:
        username: the username to disable
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    if not user.is_active:
        click.echo('User is not active')
        return

    user.is_active = False

    try:
        correct = True
        db.session.commit()
        click.echo('Correctly deactivated user')

    except Exception as e:
        correct = False
        click.echo('Failed to deactivate user:')
        click.echo(e)

    finally:
        if not correct:
            db.session.rollback()


@user.command('change-password')
@click.argument('username')
@click.option('--password', help='new password', prompt=True, hide_input=True)
def change_password(username: str, password: str):
    """Change the password of a user.

    NOTE: This process invalidates already existing user sessions.

    \b
    Args:
        username: user to change password for
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    user.password = crypto_manager.hash(password)
    user.serial = user.generate_serial()

    try:
        correct = True
        db.session.commit()
        click.echo('Password updated')

    except Exception as e:
        correct = False
        click.echo('Failed to change password:')
        click.echo(e)

    finally:
        if not correct:
            db.session.rollback()


if __name__ == '__main__':
    cli()
