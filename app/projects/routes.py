from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.projects import projects
from app.models import Project, Deal, Transaction, ActivityLog


PROJECT_STATUSES = ['planning', 'active', 'on_hold', 'completed']


def log_activity(user_id, action, entity_type=None, entity_id=None, entity_name=None):
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name
    )
    db.session.add(log)


def parse_date(value):
    """Parse a yyyy-mm-dd string from a date input. Returns None if empty/invalid."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def parse_float(value, default=0.0):
    try:
        return float(str(value).replace(',', '').replace('$', '').strip())
    except (ValueError, TypeError, AttributeError):
        return default


@projects.route('/')
@login_required
def index():
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')

    query = Project.query.filter_by(user_id=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(
            Project.name.ilike(f'%{search}%') |
            Project.address.ilike(f'%{search}%')
        )

    projects_list = query.order_by(Project.updated_at.desc()).all()

    # Total expenses logged per project (feeds the Spent column and progress bar)
    spent_rows = (
        db.session.query(
            Transaction.project_id,
            func.coalesce(func.sum(Transaction.amount), 0.0)
        )
        .join(Project, Transaction.project_id == Project.id)
        .filter(Project.user_id == current_user.id, Transaction.type == 'expense')
        .group_by(Transaction.project_id)
        .all()
    )
    spent_map = {project_id: total for project_id, total in spent_rows}

    # Map deal ids to names so linked deals display without extra queries
    deal_rows = db.session.query(Deal.id, Deal.name).filter_by(user_id=current_user.id).all()
    deal_map = {deal_id: name for deal_id, name in deal_rows}

    return render_template(
        'projects/index.html',
        title='My Projects - CredenceHub',
        projects=projects_list,
        spent_map=spent_map,
        deal_map=deal_map,
        status_filter=status_filter,
        search=search
    )


@projects.route('/new', methods=['GET', 'POST'])
@login_required
def new_project():
    deals_list = Deal.query.filter_by(user_id=current_user.id).order_by(Deal.name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        status = request.form.get('status', 'planning')
        deal_id = request.form.get('deal_id', '')
        start_date = parse_date(request.form.get('start_date', ''))
        end_date = parse_date(request.form.get('end_date', ''))
        total_budget = parse_float(request.form.get('total_budget', ''))
        notes = request.form.get('notes', '').strip()

        if not name:
            flash('Project name is required.', 'danger')
            return redirect(url_for('projects.new_project'))

        if status not in PROJECT_STATUSES:
            status = 'planning'

        if start_date and end_date and end_date < start_date:
            flash('Target end date cannot be before the start date.', 'danger')
            return redirect(url_for('projects.new_project'))

        # Only accept a deal link that belongs to the current user
        linked_deal_id = None
        if deal_id:
            deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first()
            if deal:
                linked_deal_id = deal.id

        project = Project(
            user_id=current_user.id,
            deal_id=linked_deal_id,
            name=name,
            address=address,
            status=status,
            start_date=start_date,
            end_date=end_date,
            total_budget=total_budget,
            notes=notes
        )
        db.session.add(project)
        db.session.flush()

        log_activity(
            current_user.id,
            'created a project',
            entity_type='project',
            entity_id=project.id,
            entity_name=project.name
        )
        db.session.commit()

        flash(f'Project "{project.name}" created.', 'success')
        return redirect(url_for('projects.index'))

    return render_template(
        'projects/new.html',
        title='New Project - CredenceHub',
        project=None,
        deals=deals_list,
        statuses=PROJECT_STATUSES
    )


@projects.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    deals_list = Deal.query.filter_by(user_id=current_user.id).order_by(Deal.name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        status = request.form.get('status', project.status)
        deal_id = request.form.get('deal_id', '')
        start_date = parse_date(request.form.get('start_date', ''))
        end_date = parse_date(request.form.get('end_date', ''))
        total_budget = parse_float(request.form.get('total_budget', ''))
        notes = request.form.get('notes', '').strip()

        if not name:
            flash('Project name is required.', 'danger')
            return redirect(url_for('projects.edit_project', project_id=project.id))

        if status not in PROJECT_STATUSES:
            status = project.status

        if start_date and end_date and end_date < start_date:
            flash('Target end date cannot be before the start date.', 'danger')
            return redirect(url_for('projects.edit_project', project_id=project.id))

        linked_deal_id = None
        if deal_id:
            deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first()
            if deal:
                linked_deal_id = deal.id

        project.name = name
        project.address = address
        project.status = status
        project.deal_id = linked_deal_id
        project.start_date = start_date
        project.end_date = end_date
        project.total_budget = total_budget
        project.notes = notes

        log_activity(
            current_user.id,
            'updated a project',
            entity_type='project',
            entity_id=project.id,
            entity_name=project.name
        )
        db.session.commit()

        flash(f'Project "{project.name}" updated.', 'success')
        return redirect(url_for('projects.index'))

    return render_template(
        'projects/new.html',
        title='Edit Project - CredenceHub',
        project=project,
        deals=deals_list,
        statuses=PROJECT_STATUSES
    )


@projects.route('/<int:project_id>/status', methods=['POST'])
@login_required
def update_status(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    new_status = request.form.get('status', '')

    if new_status not in PROJECT_STATUSES:
        flash('Invalid project status.', 'danger')
        return redirect(url_for('projects.index'))

    project.status = new_status
    log_activity(
        current_user.id,
        f'marked project as {new_status.replace("_", " ")}',
        entity_type='project',
        entity_id=project.id,
        entity_name=project.name
    )
    db.session.commit()

    flash(f'"{project.name}" is now {new_status.replace("_", " ").title()}.', 'success')
    return redirect(url_for('projects.index'))


@projects.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    project_name = project.name

    log_activity(
        current_user.id,
        'deleted a project',
        entity_type='project',
        entity_id=project.id,
        entity_name=project_name
    )
    db.session.delete(project)
    db.session.commit()

    flash(f'Project "{project_name}" deleted.', 'success')
    return redirect(url_for('projects.index'))