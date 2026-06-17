from flask import render_template
from flask_login import login_required
from app.deals import deals


@deals.route('/')
@login_required
def index():
    return render_template('deals/index.html', title='My Deals - CredenceHub')


@deals.route('/new')
@login_required
def new_deal():
    return render_template('deals/new.html', title='New Deal - CredenceHub')