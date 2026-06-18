import json
import secrets
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.construction import construction
from app.models import ConstructionProject, BOMItem, PermitItem, CityData, ConstructionAuditLog


def log_audit(project_id, user_id, action, details=None):
    log = ConstructionAuditLog(
        project_id=project_id,
        user_id=user_id,
        action=action,
        details=details
    )
    db.session.add(log)


def get_city_data(city, province_state):
    city_data = CityData.query.filter_by(
        city=city, province_state=province_state
    ).first()
    if not city_data:
        city_data = CityData.query.filter_by(city=city).first()
    return city_data


def generate_bom(project, city_data):
    floor_area = project.floor_area_sqft
    stories = project.stories
    foundation = project.foundation_type
    construction_type = project.construction_type
    finish_level = project.finish_level
    building_type = project.building_type

    labor_idx = city_data.labor_index if city_data else 1.0
    mat_idx = city_data.material_index if city_data else 1.0

    finish_multiplier = {
        'basic': 0.80, 'standard': 1.00, 'premium': 1.30, 'luxury': 1.75
    }.get(finish_level, 1.0)

    perimeter = (floor_area ** 0.5) * 4
    wall_area = perimeter * 9 * stories

    bom = []

    # Foundation & Structure
    if foundation == 'slab':
        concrete_cy = round(floor_area * 0.037, 1)
        bom.append({'category': 'Foundation & Structure', 'name': 'Concrete — Slab', 'quantity': concrete_cy, 'unit': 'cu yd', 'unit_cost': round(140 * mat_idx, 2)})
    elif foundation == 'basement':
        concrete_cy = round(floor_area * 0.055, 1)
        bom.append({'category': 'Foundation & Structure', 'name': 'Concrete — Basement Walls & Floor', 'quantity': concrete_cy, 'unit': 'cu yd', 'unit_cost': round(145 * mat_idx, 2)})
        rebar_lbs = round(floor_area * 1.2, 0)
        bom.append({'category': 'Foundation & Structure', 'name': 'Rebar', 'quantity': rebar_lbs, 'unit': 'lbs', 'unit_cost': round(0.65 * mat_idx, 2)})
    else:
        concrete_cy = round(floor_area * 0.025, 1)
        bom.append({'category': 'Foundation & Structure', 'name': 'Concrete — Crawl Space Footings', 'quantity': concrete_cy, 'unit': 'cu yd', 'unit_cost': round(138 * mat_idx, 2)})

    if construction_type == 'wood_frame':
        lumber_bf = round(floor_area * stories * 3.5, 0)
        bom.append({'category': 'Foundation & Structure', 'name': 'Structural Lumber', 'quantity': lumber_bf, 'unit': 'board ft', 'unit_cost': round(0.85 * mat_idx, 2)})
    elif construction_type == 'concrete_block':
        blocks = round(wall_area * 1.125, 0)
        bom.append({'category': 'Foundation & Structure', 'name': 'Concrete Blocks', 'quantity': blocks, 'unit': 'units', 'unit_cost': round(2.20 * mat_idx, 2)})
    else:
        steel_tons = round(floor_area * stories * 0.006, 1)
        bom.append({'category': 'Foundation & Structure', 'name': 'Structural Steel', 'quantity': steel_tons, 'unit': 'tons', 'unit_cost': round(1800 * mat_idx, 2)})

    # Framing & Walls
    lumber_studs = round(wall_area / 1.33, 0)
    bom.append({'category': 'Framing & Walls', 'name': 'Framing Lumber (2x6)', 'quantity': lumber_studs, 'unit': 'linear ft', 'unit_cost': round(1.20 * mat_idx, 2)})
    osb_sheets = round(wall_area / 32, 0)
    bom.append({'category': 'Framing & Walls', 'name': 'OSB Sheathing', 'quantity': osb_sheets, 'unit': 'sheets', 'unit_cost': round(28 * mat_idx, 2)})
    insulation_sqft = round(wall_area * 1.1, 0)
    bom.append({'category': 'Framing & Walls', 'name': 'Insulation (R-20)', 'quantity': insulation_sqft, 'unit': 'sq ft', 'unit_cost': round(0.75 * mat_idx, 2)})
    drywall_sheets = round((wall_area + floor_area * stories) / 32, 0)
    bom.append({'category': 'Framing & Walls', 'name': 'Drywall / Gypsum Board', 'quantity': drywall_sheets, 'unit': 'sheets', 'unit_cost': round(15 * mat_idx, 2)})

    # Roofing
    roof_sqft = round(floor_area * 1.15, 0)
    bom.append({'category': 'Roofing', 'name': 'Roof Decking (OSB)', 'quantity': round(roof_sqft / 32, 0), 'unit': 'sheets', 'unit_cost': round(28 * mat_idx, 2)})
    bom.append({'category': 'Roofing', 'name': 'Roofing Underlayment', 'quantity': round(roof_sqft / 400, 1), 'unit': 'rolls', 'unit_cost': round(85 * mat_idx, 2)})
    if finish_level in ['basic', 'standard']:
        bom.append({'category': 'Roofing', 'name': 'Asphalt Shingles', 'quantity': round(roof_sqft / 100, 0), 'unit': 'squares', 'unit_cost': round(120 * mat_idx * finish_multiplier, 2)})
    else:
        bom.append({'category': 'Roofing', 'name': 'Metal Roofing', 'quantity': round(roof_sqft, 0), 'unit': 'sq ft', 'unit_cost': round(4.50 * mat_idx * finish_multiplier, 2)})
    bom.append({'category': 'Roofing', 'name': 'Fascia & Soffit', 'quantity': round(perimeter, 0), 'unit': 'linear ft', 'unit_cost': round(8 * mat_idx, 2)})

    # Windows & Doors
    window_count = max(6, round(floor_area / 120 * stories, 0))
    bom.append({'category': 'Windows & Doors', 'name': 'Windows (standard size)', 'quantity': window_count, 'unit': 'units', 'unit_cost': round(450 * mat_idx * finish_multiplier, 2)})
    bom.append({'category': 'Windows & Doors', 'name': 'Exterior Doors', 'quantity': 2, 'unit': 'units', 'unit_cost': round(800 * mat_idx * finish_multiplier, 2)})
    interior_doors = max(4, round(floor_area / 200 * stories, 0))
    bom.append({'category': 'Windows & Doors', 'name': 'Interior Doors', 'quantity': interior_doors, 'unit': 'units', 'unit_cost': round(280 * mat_idx * finish_multiplier, 2)})

    # Electrical
    bom.append({'category': 'Electrical', 'name': 'Electrical Panel (200A)', 'quantity': 1, 'unit': 'unit', 'unit_cost': round(1800 * labor_idx, 2)})
    wiring_lf = round(floor_area * stories * 3.5, 0)
    bom.append({'category': 'Electrical', 'name': 'Romex Wiring', 'quantity': wiring_lf, 'unit': 'linear ft', 'unit_cost': round(0.55 * mat_idx, 2)})
    outlets = round(floor_area * stories / 50, 0)
    bom.append({'category': 'Electrical', 'name': 'Outlets & Switches', 'quantity': outlets, 'unit': 'units', 'unit_cost': round(45 * labor_idx, 2)})
    fixtures = round(floor_area * stories / 80, 0)
    bom.append({'category': 'Electrical', 'name': 'Light Fixtures', 'quantity': fixtures, 'unit': 'units', 'unit_cost': round(85 * mat_idx * finish_multiplier, 2)})

    # Plumbing
    bathrooms = max(1, round(floor_area / 500, 0))
    pipe_lf = round(floor_area * stories * 2.2, 0)
    bom.append({'category': 'Plumbing', 'name': 'PEX Piping', 'quantity': pipe_lf, 'unit': 'linear ft', 'unit_cost': round(0.85 * mat_idx, 2)})
    bom.append({'category': 'Plumbing', 'name': 'Toilets', 'quantity': bathrooms, 'unit': 'units', 'unit_cost': round(380 * mat_idx * finish_multiplier, 2)})
    bom.append({'category': 'Plumbing', 'name': 'Sinks & Faucets', 'quantity': bathrooms + 1, 'unit': 'units', 'unit_cost': round(320 * mat_idx * finish_multiplier, 2)})
    bom.append({'category': 'Plumbing', 'name': 'Bathtub / Shower', 'quantity': bathrooms, 'unit': 'units', 'unit_cost': round(850 * mat_idx * finish_multiplier, 2)})
    bom.append({'category': 'Plumbing', 'name': 'Water Heater', 'quantity': 1, 'unit': 'unit', 'unit_cost': round(1200 * mat_idx, 2)})

    # HVAC
    btu = round(floor_area * stories * 25, 0)
    bom.append({'category': 'HVAC', 'name': f'Furnace / AC ({int(btu/12000)} ton)', 'quantity': 1, 'unit': 'unit', 'unit_cost': round(4500 * labor_idx * finish_multiplier, 2)})
    ductwork_lf = round(floor_area * stories * 0.8, 0)
    bom.append({'category': 'HVAC', 'name': 'Ductwork', 'quantity': ductwork_lf, 'unit': 'linear ft', 'unit_cost': round(12 * labor_idx, 2)})

    # Finishes
    bom.append({'category': 'Finishes', 'name': 'Flooring', 'quantity': round(floor_area * stories, 0), 'unit': 'sq ft', 'unit_cost': round(5.50 * mat_idx * finish_multiplier, 2)})
    paint_gallons = round(wall_area / 350, 0)
    bom.append({'category': 'Finishes', 'name': 'Paint (Interior & Exterior)', 'quantity': paint_gallons, 'unit': 'gallons', 'unit_cost': round(42 * mat_idx * finish_multiplier, 2)})
    cabinet_lf = round(10 + (floor_area / 300), 0)
    bom.append({'category': 'Finishes', 'name': 'Kitchen Cabinets', 'quantity': cabinet_lf, 'unit': 'linear ft', 'unit_cost': round(280 * mat_idx * finish_multiplier, 2)})
    bom.append({'category': 'Finishes', 'name': 'Countertops', 'quantity': round(cabinet_lf * 1.5, 0), 'unit': 'sq ft', 'unit_cost': round(65 * mat_idx * finish_multiplier, 2)})
    bathroom_tile = round(bathrooms * 80, 0)
    bom.append({'category': 'Finishes', 'name': 'Bathroom Tile', 'quantity': bathroom_tile, 'unit': 'sq ft', 'unit_cost': round(8 * mat_idx * finish_multiplier, 2)})

    return bom


def generate_permits(city, province_state, country, floor_area):
    base_permits = [
        {'name': 'Building Permit', 'estimated_fee': round(floor_area * 1.20, 0), 'processing_time': '4-8 weeks', 'notes': 'Required for all new construction and major renovations', 'is_required': True},
        {'name': 'Development Permit', 'estimated_fee': round(floor_area * 0.50, 0), 'processing_time': '6-12 weeks', 'notes': 'Required before building permit in most municipalities', 'is_required': True},
        {'name': 'Electrical Permit', 'estimated_fee': round(floor_area * 0.25, 0), 'processing_time': '1-2 weeks', 'notes': 'Required for all electrical work', 'is_required': True},
        {'name': 'Plumbing Permit', 'estimated_fee': round(floor_area * 0.20, 0), 'processing_time': '1-2 weeks', 'notes': 'Required for all plumbing installations', 'is_required': True},
        {'name': 'Gas Permit', 'estimated_fee': 350, 'processing_time': '1 week', 'notes': 'Required if gas appliances are installed', 'is_required': True},
        {'name': 'Occupancy Certificate', 'estimated_fee': 250, 'processing_time': '1-2 weeks after completion', 'notes': 'Required before occupying the building', 'is_required': True},
        {'name': 'Site Plan Approval', 'estimated_fee': 800, 'processing_time': '3-6 weeks', 'notes': 'Site plan showing setbacks and property lines', 'is_required': True},
        {'name': 'Survey Certificate', 'estimated_fee': 1200, 'processing_time': '2-4 weeks', 'notes': 'Land survey required for permit applications', 'is_required': True},
        {'name': 'Engineered Drawings', 'estimated_fee': round(floor_area * 1.50, 0), 'processing_time': '3-6 weeks', 'notes': 'Structural engineering drawings required', 'is_required': True},
        {'name': 'Environmental Assessment', 'estimated_fee': 2500, 'processing_time': '4-8 weeks', 'notes': 'May be required depending on site conditions', 'is_required': False},
    ]
    return base_permits


@construction.route('/')
@login_required
def index():
    projects = ConstructionProject.query.filter_by(
        user_id=current_user.id
    ).order_by(ConstructionProject.updated_at.desc()).all()

    cities = CityData.query.order_by(CityData.country, CityData.city).all()

    return render_template(
        'construction/index.html',
        title='Construction Calculator - CredenceHub',
        projects=projects,
        cities=cities
    )


@construction.route('/new', methods=['GET', 'POST'])
@login_required
def new_project():
    cities = CityData.query.order_by(CityData.country, CityData.city).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        province_state = request.form.get('province_state', '').strip()
        country = request.form.get('country', 'CA')
        building_type = request.form.get('building_type', 'sfh')
        stories = int(request.form.get('stories', 1))
        floor_area = float(request.form.get('floor_area', 0))
        foundation_type = request.form.get('foundation_type', 'slab')
        construction_type = request.form.get('construction_type', 'wood_frame')
        finish_level = request.form.get('finish_level', 'standard')
        contingency_pct = float(request.form.get('contingency_pct', 10))

        if not name or not city or floor_area <= 0:
            flash('Project name, city, and floor area are required.', 'danger')
            return render_template('construction/new.html', cities=cities)

        project = ConstructionProject(
            user_id=current_user.id,
            name=name,
            city=city,
            province_state=province_state,
            country=country,
            building_type=building_type,
            stories=stories,
            floor_area_sqft=floor_area,
            foundation_type=foundation_type,
            construction_type=construction_type,
            finish_level=finish_level,
            contingency_pct=contingency_pct
        )
        db.session.add(project)
        db.session.flush()

        city_data = get_city_data(city, province_state)
        bom_items = generate_bom(project, city_data)
        for item in bom_items:
            bom = BOMItem(
                project_id=project.id,
                category=item['category'],
                name=item['name'],
                quantity=item['quantity'],
                unit=item['unit'],
                unit_cost=item['unit_cost']
            )
            db.session.add(bom)

        permit_items = generate_permits(city, province_state, country, floor_area)
        for item in permit_items:
            permit = PermitItem(
                project_id=project.id,
                name=item['name'],
                estimated_fee=item['estimated_fee'],
                processing_time=item['processing_time'],
                notes=item['notes'],
                is_required=item['is_required']
            )
            db.session.add(permit)

        log_audit(project.id, current_user.id, 'Project created', f'City: {city}, Area: {floor_area} sqft')
        db.session.commit()

        flash('Construction project created successfully.', 'success')
        return redirect(url_for('construction.view_project', project_id=project.id))

    return render_template('construction/new.html', title='New Construction Project - CredenceHub', cities=cities)


@construction.route('/<int:project_id>')
@login_required
def view_project(project_id):
    project = ConstructionProject.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()

    city_data = get_city_data(project.city, project.province_state)
    bom_items = project.bom_items.order_by(BOMItem.category).all()
    permit_items = project.permit_items.all()
    audit_logs = project.audit_logs.order_by(ConstructionAuditLog.created_at.desc()).limit(20).all()

    categories = {}
    total_materials = 0
    for item in bom_items:
        line_total = item.quantity * item.unit_cost
        total_materials += line_total
        if item.category not in categories:
            categories[item.category] = {'items': [], 'subtotal': 0}
        categories[item.category]['items'].append(item)
        categories[item.category]['subtotal'] += line_total

    total_permits = sum(p.estimated_fee for p in permit_items if p.is_required)
    land_cost = city_data.land_cost_sqft * project.floor_area_sqft if city_data else 0
    labor_cost = total_materials * 0.65
    hard_costs = total_materials + labor_cost
    soft_costs = total_permits
    contingency = (hard_costs + soft_costs) * (project.contingency_pct / 100)
    grand_total = land_cost + hard_costs + soft_costs + contingency
    cost_per_sqft = grand_total / project.floor_area_sqft if project.floor_area_sqft > 0 else 0

    return render_template(
        'construction/view.html',
        title=f'{project.name} - CredenceHub',
        project=project,
        city_data=city_data,
        categories=categories,
        permit_items=permit_items,
        audit_logs=audit_logs,
        total_materials=total_materials,
        labor_cost=labor_cost,
        hard_costs=hard_costs,
        soft_costs=soft_costs,
        land_cost=land_cost,
        contingency=contingency,
        grand_total=grand_total,
        cost_per_sqft=cost_per_sqft,
        total_permits=total_permits
    )


@construction.route('/<int:project_id>/update-bom', methods=['POST'])
@login_required
def update_bom(project_id):
    project = ConstructionProject.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()

    data = request.get_json()
    item_id = data.get('item_id')
    field = data.get('field')
    value = float(data.get('value', 0))

    item = BOMItem.query.filter_by(id=item_id, project_id=project.id).first_or_404()

    if field == 'quantity':
        item.quantity = value
    elif field == 'unit_cost':
        item.unit_cost = value
        item.is_overridden = True

    log_audit(project.id, current_user.id, f'BOM item updated: {item.name}', f'{field} changed to {value}')
    db.session.commit()

    return jsonify({'success': True, 'line_total': round(item.quantity * item.unit_cost, 2)})


@construction.route('/<int:project_id>/share', methods=['POST'])
@login_required
def share_project(project_id):
    project = ConstructionProject.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()

    if not project.share_token:
        project.share_token = secrets.token_urlsafe(32)
        db.session.commit()

    share_url = url_for('construction.shared_report', token=project.share_token, _external=True)
    return jsonify({'success': True, 'url': share_url})


@construction.route('/shared/<token>')
def shared_report(token):
    project = ConstructionProject.query.filter_by(share_token=token).first_or_404()
    city_data = get_city_data(project.city, project.province_state)
    bom_items = project.bom_items.order_by(BOMItem.category).all()
    permit_items = project.permit_items.all()

    categories = {}
    total_materials = 0
    for item in bom_items:
        line_total = item.quantity * item.unit_cost
        total_materials += line_total
        if item.category not in categories:
            categories[item.category] = {'items': [], 'subtotal': 0}
        categories[item.category]['items'].append(item)
        categories[item.category]['subtotal'] += line_total

    total_permits = sum(p.estimated_fee for p in permit_items if p.is_required)
    land_cost = city_data.land_cost_sqft * project.floor_area_sqft if city_data else 0
    labor_cost = total_materials * 0.65
    hard_costs = total_materials + labor_cost
    soft_costs = total_permits
    contingency = (hard_costs + soft_costs) * (project.contingency_pct / 100)
    grand_total = land_cost + hard_costs + soft_costs + contingency
    cost_per_sqft = grand_total / project.floor_area_sqft if project.floor_area_sqft > 0 else 0

    return render_template(
        'construction/shared.html',
        project=project,
        city_data=city_data,
        categories=categories,
        permit_items=permit_items,
        total_materials=total_materials,
        labor_cost=labor_cost,
        hard_costs=hard_costs,
        soft_costs=soft_costs,
        land_cost=land_cost,
        contingency=contingency,
        grand_total=grand_total,
        cost_per_sqft=cost_per_sqft
    )