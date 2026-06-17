from flask import render_template
from flask_login import login_required, current_user
from app.admin import admin


@admin.route('/')
@login_required
def index():
    if not current_user.is_admin:
        from flask import abort
        abort(403)
    return render_template('admin/index.html', title='Admin Panel - CredenceHub')