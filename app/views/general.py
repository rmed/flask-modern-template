# -*- coding: utf-8 -*-

"""General views."""

from flask import Blueprint, render_template
from flask_login import login_required


bp_general = Blueprint('general', __name__)


@bp_general.route('/')
@login_required
def home():
    """Show home."""
    return render_template('general/home.html')
