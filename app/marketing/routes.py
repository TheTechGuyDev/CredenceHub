from flask import render_template
from flask_login import login_required
from app.marketing import marketing


@marketing.route('/')
@login_required
def index():
    return render_template('marketing/index.html', title='Marketing Tools - CredenceHub')