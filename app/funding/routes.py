from flask import render_template
from flask_login import login_required
from app.funding import funding


@funding.route('/')
@login_required
def index():
    return render_template('funding/index.html', title='Funding Proposals - CredenceHub')