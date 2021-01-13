# -*- coding: utf-8 -*-

"""Authentication views."""

import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, \
    request, url_for
from flask_babel import _
from flask_login import confirm_login, current_user, login_user, logout_user, \
    login_required
from sqlalchemy import or_, exc as dbexc

from .. import db, crypto_manager
from ..forms import InviteForm, LoginForm, ForgotPasswordForm, \
    ReauthenticationForm, PasswordResetForm, SignupForm
from ..models import Invitation, User
from ..util import is_safe_url, send_email


bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    """Log the user in."""
    form = LoginForm()

    if form.validate_on_submit():
        # Check credentials
        user = (
            User.query
            .filter(
                or_(
                    User.username==form.identity.data,
                    User.email==form.identity.data
                )
            )
            .filter(User.is_active==True)
        ).first()

        if not user or not crypto_manager.verify(form.password.data, user.password):
            # Show invalid credentials message
            flash(_('Invalid credentials'), 'error')

            return render_template('auth/login.html', form=form)

        # Log the user in
        if login_user(user, remember=form.remember_me.data):
            flash(_('Logged in successfully'), 'success')

            # Validate destination
            next_url = request.args.get('next')

            if next_url and is_safe_url(next_url):
                return redirect(next_url)

            return redirect(url_for('general.home'))

        # User is not allowed
        flash(_('Invalid credentials'), 'error')

    return render_template('auth/login.html', form=form)


@bp_auth.route("/logout")
@login_required
def logout():
    """Log the user out."""
    logout_user()

    return redirect(url_for('auth.login'))


@bp_auth.route('/reauthenticate', methods=['GET', 'POST'])
@login_required
def reauthenticate():
    """Ask the user to confirm their password."""
    form = ReauthenticationForm()

    # Logout if not active
    if not current_user.is_active:
        logout_user()
        flash(_('User is not active'), 'warning')

        return redirect(url_for('auth.login'))


    if form.validate_on_submit():
        # Check credentials
        if crypto_manager.verify(form.password.data, current_user.password):
            # Show invalid credentials message
            flash(_('Invalid credentials'), 'error')

            return render_template('auth/reauthenticate.html', form=form)

        # Refresh session
        confirm_login()

        # Validate destination
        next_url = request.args.get('next')

        if next_url and is_safe_url(next_url):
            return redirect(next_url)

    return render_template('auth/reauthenticate.html', form=form)


@bp_auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Show a form to request a password reset token.

    This does not tell the user whether the emails is valid or not. In
    addition, if the user already had a password reset token, it will be
    overwritten.
    """
    if current_user.is_authenticated:
        # Authenticated user cannot do this
        logout_user()

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        # Verify user (must be active)
        user = (
            User.query
            .filter_by(email=form.email.data)
            .filter_by(is_active=True)
        ).first()

        if not user:
            # Don't let the user know
            flash(_('A password reset token has been sent'), 'success')
            return render_template('auth/forgot_password.html', form=form)

        # Set token
        user.password_reset_token = user.generate_reset_token()
        user.password_reset_expiration = (
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )

        try:
            correct = True
            db.session.commit()

            # Send notification email
            send_email(
                _('Password reset'),
                recipients=[user.email],
                body=render_template(
                    'emails/auth/forgot_password.txt',
                    user=user
                )
            )

            flash(_('A password reset token has been sent'), 'success')
            return render_template('auth/forgot_password.html', form=form)

        except Exception:
            correct = False
            current_app.logger.exception(
                'Failed to update password reset token for %s' % user.username
            )

            # Don't let the user know
            flash(_('A password reset token has been sent'), 'success')
            return render_template('auth/forgot_password.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('auth/forgot_password.html', form=form)


@bp_auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Show a form to reset account password.

    Args:
        token (str): Random token mailed to the user.
    """
    if current_user.is_authenticated:
        # Authenticated user cannot do this
        logout_user()

    # Verify token
    now = datetime.datetime.utcnow()
    user = (
        User.query
        .filter_by(password_reset_token=token)
        .filter_by(is_active=True)
        .filter(User.password_reset_expiration >= now)
    ).first()

    if not user:
        flash(_('Invalid password reset token provided'), 'error')
        return redirect(url_for('auth.login'))

    # Show form
    form = PasswordResetForm()

    if form.validate_on_submit():
        # Update user
        user.password = crypto_manager.hash(form.password.data)
        user.password_reset_token = None
        user.password_password_reset_expiration = None
        user.serial = user.generate_serial()

        try:
            correct = True
            db.session.commit()

            # Send notification email
            send_email(
                _('Password reset notification'),
                recipients=[user.email],
                body=render_template('email/auth/password_changed.txt')
            )

            flash(_('Password updated, you may now login'), 'success')
            return redirect(url_for('auth.login'))

        except Exception:
            correct = False
            current_app.logger.exception('Failed to reset user password')

            flash(_('Error updating password, contact an admin'), 'error')
            return render_template('auth/reset_password.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('auth/reset_password.html', form=form)


@bp_auth.route('/invite', methods=['GET', 'POST'])
@login_required
def invite():
    """Generate and send an invite token that can be used to sign up."""
    if not current_user.is_active:
        logout_user()
        return redirect(url_for('auth.login'))

    form = InviteForm()

    if form.validate_on_submit():
        if current_user.invitations <= 0:
            flash(_('You have no invitations left'), 'error')

            return render_template(
                'auth/invite.html',
                form=form
            )

        new_invitation = Invitation(owner_id=current_user.id)
        new_invitation.token = new_invitation.generate_token()

        while Invitation.get_by_token(new_invitation.token):
            new_invitation.token = new_invitation.generate_token()

        current_user.invitations -= 1

        try:
            correct = True
            db.session.add(new_invitation)

            body = render_template(
                'emails/auth/invite.txt',
                user=current_user,
                invitation=new_invitation
            )

            current_app.logger.debug('Generated email:\n%s' % body)

            send_email(
                _('%(site)s invitation', site=current_app.config['SITENAME']),
                recipients=[form.email.data],
                body=body
            )

            current_app.logger.info(
                '%s sent an invitation to %s' % (current_user.username, form.email.data)
            )

            db.session.commit()

            flash(_('Invitation sent!'), 'success')

            return redirect(url_for('auth.invite'))

        except Exception:
            correct = False
            current_app.logger.exception('Failed to create or send invitation')

            flash(_('Failed to create or send invitation'), 'error')

        finally:
            if not correct:
                db.session.rollback()


    return render_template(
        'auth/invite.html',
        form=form
    )


@bp_auth.route('/signup/<token>', methods=['GET', 'POST'])
def signup(token):
    """Sign up using an invite token.

    Args:
        token (str): Token received in the invitation.
    """
    if current_user.is_authenticated:
        # Authenticated users cannot do this
        logout_user()

    invitation = Invitation.get_by_token(token)

    if not invitation or invitation.expiration <= datetime.datetime.utcnow() or \
            invitation.user_id is not None:

        flash(_('Token is not valid'), 'error')
        return redirect(url_for('auth.login'))

    form = SignupForm()

    if form.validate_on_submit():
        new_user = User(is_active=True)
        form.populate_obj(new_user)

        new_user.password = crypto_manager.hash(form.plain_password.data)
        invitation.user = new_user

        try:
            correct = True

            db.session.add(new_user)
            db.session.commit()

            flash(_('User created correctly, please login'), 'success')

            return redirect(url_for('auth.login'))

        except dbexc.IntegrityError:
            correct = False
            current_app.logger.exception('Integrity error creating user')

            flash(_('A user with those details already exists'), 'error')

        except Exception:
            correct = False
            current_app.logger.exception('Failed to create user')

            flash(_('Failed to create user'), 'error')

        finally:
            if not correct:
                db.session.rollback()

    return render_template(
        'auth/signup.html',
        form=form
    )
