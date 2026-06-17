from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import dashboard
from app.models import Deal, Project, ConstructionProject, ActivityLog, Notification


@dashboard.route('/')
@dashboard.route('/index')
@login_required
def index():
    # KPI data
    total_deals = Deal.query.filter_by(
        user_id=current_user.id
    ).count()

    active_deals = Deal.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).count()

    active_projects = Project.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).count()

    construction_projects = ConstructionProject.query.filter_by(
        user_id=current_user.id
    ).count()

    # Recent deals
    recent_deals = Deal.query.filter_by(
        user_id=current_user.id
    ).order_by(Deal.updated_at.desc()).limit(5).all()

    # Recent projects
    recent_projects = Project.query.filter_by(
        user_id=current_user.id
    ).order_by(Project.updated_at.desc()).limit(5).all()

    # Recent activity
    recent_activity = ActivityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()

    # Unread notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        title='Dashboard - CredenceHub',
        total_deals=total_deals,
        active_deals=active_deals,
        active_projects=active_projects,
        construction_projects=construction_projects,
        recent_deals=recent_deals,
        recent_projects=recent_projects,
        recent_activity=recent_activity,
        notifications=notifications
    )