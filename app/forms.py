# -*- coding: utf-8 -*-

"""Form definitions."""

import pytz

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, \
        StringField, SubmitField
from wtforms import validators

from .bootstrap import LANGUAGES, LANGUAGES_LOCALIZED


# Authentication forms
class LoginForm(FlaskForm):
    """Application login form."""
    identity = StringField(
        _l('Username or email'),
        validators=[
            validators.InputRequired(_l('Identity is required')),
        ]
    )

    password = PasswordField(
        _l('Password'),
        validators=[
            validators.InputRequired(_l('Password is required')),
        ]
    )

    remember_me = BooleanField(_l('Remember me'))

    submit = SubmitField(_l('Sign in'))


class ForgotPasswordForm(FlaskForm):
    """Form to request password reset token."""
    email = StringField(
        _l('Email'),
        validators=[
            validators.InputRequired(_l('Email is required')),
            validators.Email(_l('Invalid Email'))
        ]
    )

    submit = SubmitField(_l('Reset password'))


class ReauthenticationForm(FlaskForm):
    """Reauthentication form."""
    password = PasswordField(
        _l('Password'),
        validators=[
            validators.InputRequired(_l('Password is required')),
        ]
    )

    submit = SubmitField(_l('Sign in'))


class PasswordResetForm(FlaskForm):
    """Reset password form."""
    password = PasswordField(
        _l('New password'),
        validators=[validators.InputRequired(_l('Password is required'))]
    )

    retype_password = PasswordField(
        _l('Retype new password'),
        validators=[
            validators.EqualTo(
                'password',
                message=_l('Passwords did not match')
            )
        ]
    )

    submit = SubmitField(_l('Reset password'))


class SignupForm(FlaskForm):
    """User signup form."""
    username = StringField(
        _l('Username'),
        [validators.Length(min=4, max=50), validators.InputRequired()],
        description=_l('must be unique')
    )

    email = StringField(
        _l('Email'),
        [validators.Length(min=4, max=255), validators.InputRequired()],
        description=_l('must be unique')
    )

    plain_password = PasswordField(
        _l('Password'),
        [validators.Length(min=8, max=255), validators.InputRequired()],
    )

    confirm_password = PasswordField(
        _l('Confirm password'),
        validators=[
            validators.EqualTo(
                'plain_password',
                message=_l('Passwords did not match')
            )
        ]
    )

    locale = SelectField(
        _l('Locale'),
        choices=list(zip(LANGUAGES, LANGUAGES_LOCALIZED))
    )

    timezone = SelectField(
        _l('Timezone'),
        choices=[(t, t) for t in pytz.common_timezones],
        default='en'
    )

    submit = SubmitField(_l('Submit'))


class InviteForm(FlaskForm):
    """Form for inviting users by email."""
    email = StringField(
        _l('Email'),
        validators=[
            validators.InputRequired(_l('Email is required')),
            validators.Email(_l('Invalid Email'))
        ]
    )

    submit = SubmitField(_l('Send'))
