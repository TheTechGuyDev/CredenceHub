from flask import render_template
from flask_login import login_required
from app.construction import construction


@construction.route('/')
@login_required
def index():
    return render_template('construction/index.html', title='Construction Calculator - CredenceHub')