from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('main/landing.html', title='CredenceHub - Real Estate Investment & Construction Analysis Platform')


@main.route('/pricing')
def pricing():
    return render_template('main/pricing.html', title='Pricing - CredenceHub')


@main.route('/privacy')
def privacy():
    return render_template('main/privacy.html', title='Privacy Policy - CredenceHub')


@main.route('/terms')
def terms():
    return render_template('main/terms.html', title='Terms of Service - CredenceHub')


@main.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact - CredenceHub')