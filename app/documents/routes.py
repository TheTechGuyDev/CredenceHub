from flask import render_template
from flask_login import login_required
from app.documents import documents


@documents.route('/')
@login_required
def index():
    return render_template('documents/index.html', title='Documents - CredenceHub')