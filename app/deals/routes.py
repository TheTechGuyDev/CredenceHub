import json
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.deals import deals
from app.models import Deal, DealScenario, ActivityLog


def log_activity(user_id, action, entity_type=None, entity_id=None, entity_name=None):
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name
    )
    db.session.add(log)


@deals.route('/')
@login_required
def index():
    status_filter = request.args.get('status', 'all')
    strategy_filter = request.args.get('strategy', 'all')
    search = request.args.get('search', '')

    query = Deal.query.filter_by(user_id=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if strategy_filter != 'all':
        query = query.filter_by(strategy=strategy_filter)
    if search:
        query = query.filter(
            Deal.name.ilike(f'%{search}%') |
            Deal.address.ilike(f'%{search}%')
        )

    deals_list = query.order_by(Deal.updated_at.desc()).all()

    return render_template(
        'deals/index.html',
        title='Deal Analysis - CredenceHub',
        deals=deals_list,
        status_filter=status_filter,
        strategy_filter=strategy_filter,
        search=search
    )


@deals.route('/new', methods=['GET', 'POST'])
@login_required
def new_deal():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        strategy = request.form.get('strategy', '')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        province_state = request.form.get('province_state', '').strip()
        notes = request.form.get('notes', '').strip()

        if not name or not strategy:
            flash('Deal name and strategy are required.', 'danger')
            return redirect(url_for('deals.new_deal'))

        deal = Deal(
            user_id=current_user.id,
            name=name,
            strategy=strategy,
            address=address,
            city=city,
            province_state=province_state,
            notes=notes,
            status='active',
            inputs=json.dumps({}),
            outputs=json.dumps({})
        )
        db.session.add(deal)
        db.session.flush()

        log_activity(current_user.id, 'Created new deal', 'deal', deal.id, name)
        db.session.commit()

        flash('Deal created successfully.', 'success')
        return redirect(url_for('deals.edit_deal', deal_id=deal.id))

    return render_template('deals/new.html', title='New Deal - CredenceHub')


@deals.route('/<int:deal_id>')
@login_required
def view_deal(deal_id):
    deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first_or_404()
    inputs = json.loads(deal.inputs or '{}')
    outputs = json.loads(deal.outputs or '{}')
    scenarios = deal.scenarios.all()
    return render_template(
        'deals/view.html',
        title=f'{deal.name} - CredenceHub',
        deal=deal,
        inputs=inputs,
        outputs=outputs,
        scenarios=scenarios
    )


@deals.route('/<int:deal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deal(deal_id):
    deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        action = request.form.get('action', 'save')

        deal.name = request.form.get('name', deal.name).strip()
        deal.address = request.form.get('address', '').strip()
        deal.city = request.form.get('city', '').strip()
        deal.province_state = request.form.get('province_state', '').strip()
        deal.notes = request.form.get('notes', '').strip()
        deal.status = request.form.get('status', deal.status)

        inputs = {}
        for key, value in request.form.items():
            if key.startswith('input_'):
                field = key.replace('input_', '')
                try:
                    inputs[field] = float(value) if value else 0
                except ValueError:
                    inputs[field] = value

        deal.inputs = json.dumps(inputs)

        from app.utils.calculators import calculate_deal
        outputs = calculate_deal(deal.strategy, inputs)
        deal.outputs = json.dumps(outputs)

        log_activity(current_user.id, 'Updated deal', 'deal', deal.id, deal.name)
        db.session.commit()

        flash('Deal saved successfully.', 'success')
        return redirect(url_for('deals.edit_deal', deal_id=deal.id))

    inputs = json.loads(deal.inputs or '{}')
    outputs = json.loads(deal.outputs or '{}')
    scenarios = deal.scenarios.all()

    return render_template(
        'deals/edit.html',
        title=f'Edit {deal.name} - CredenceHub',
        deal=deal,
        inputs=inputs,
        outputs=outputs,
        scenarios=scenarios
    )


@deals.route('/<int:deal_id>/delete', methods=['POST'])
@login_required
def delete_deal(deal_id):
    deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first_or_404()
    name = deal.name
    db.session.delete(deal)
    log_activity(current_user.id, 'Deleted deal', 'deal', None, name)
    db.session.commit()
    flash('Deal deleted.', 'info')
    return redirect(url_for('deals.index'))


@deals.route('/<int:deal_id>/calculate', methods=['POST'])
@login_required
def calculate(deal_id):
    deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first_or_404()

    data = request.get_json()
    inputs = data.get('inputs', {})

    from app.utils.calculators import calculate_deal
    outputs = calculate_deal(deal.strategy, inputs)

    deal.inputs = json.dumps(inputs)
    deal.outputs = json.dumps(outputs)
    db.session.commit()

    return jsonify({'success': True, 'outputs': outputs})


@deals.route('/<int:deal_id>/status', methods=['POST'])
@login_required
def update_status(deal_id):
    deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first_or_404()
    new_status = request.form.get('status')
    if new_status in ['active', 'archived', 'sold']:
        deal.status = new_status
        db.session.commit()
        flash(f'Deal marked as {new_status}.', 'success')
    return redirect(url_for('deals.view_deal', deal_id=deal.id))


@deals.route('/<int:deal_id>/scenario/save', methods=['POST'])
@login_required
def save_scenario(deal_id):
    deal = Deal.query.filter_by(id=deal_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    scenario_name = data.get('name', 'Scenario')
    inputs = data.get('inputs', {})

    from app.utils.calculators import calculate_deal
    outputs = calculate_deal(deal.strategy, inputs)

    scenario = DealScenario(
        deal_id=deal.id,
        name=scenario_name,
        inputs=json.dumps(inputs),
        outputs=json.dumps(outputs)
    )
    db.session.add(scenario)
    db.session.commit()

    return jsonify({'success': True, 'scenario_id': scenario.id, 'name': scenario_name})