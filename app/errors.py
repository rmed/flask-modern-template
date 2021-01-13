# -*- coding: utf-8 -*-

"""HTTP error handling."""

from flask import redirect, render_template, url_for
from flask_login import current_user


def forbidden_403(e):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('errors/403.html'), 403

def not_found_404(e):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('errors/404.html'), 404

def server_error_500(e):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('errors/500.html'), 500
