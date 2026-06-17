from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─────────────────────────────────────────
# USER & AUTHENTICATION
# ─────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    plan = db.Column(db.String(20), default='lite')  # lite, premium, pro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    onboarding_complete = db.Column(db.Boolean, default=False)

    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    deals = db.relationship('Deal', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    construction_projects = db.relationship('ConstructionProject', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    buyer_contacts = db.relationship('BuyerContact', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    lender_contacts = db.relationship('LenderContact', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    def is_premium(self):
        return self.plan in ['premium', 'pro']

    def is_pro(self):
        return self.plan == 'pro'


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    company_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    province_state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(10), default='CA')
    avatar_url = db.Column(db.String(255), nullable=True)
    investor_role = db.Column(db.String(50), nullable=True)  # wholesaler, flipper, developer, builder, investor
    experience_level = db.Column(db.String(20), nullable=True)  # beginner, intermediate, advanced
    target_markets = db.Column(db.Text, nullable=True)  # JSON string of cities
    team_size = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name or self.last_name or 'User'


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('TeamMember', backref='team', lazy='dynamic', cascade='all, delete-orphan')


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # admin, editor, viewer
    status = db.Column(db.String(20), default='pending')  # pending, active
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_at = db.Column(db.DateTime, nullable=True)


# ─────────────────────────────────────────
# DEAL ANALYSIS
# ─────────────────────────────────────────

class Deal(db.Model):
    __tablename__ = 'deals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    province_state = db.Column(db.String(100), nullable=True)
    postal_zip = db.Column(db.String(20), nullable=True)
    strategy = db.Column(db.String(30), nullable=False)  # wholesale, fix_flip, brrrr, construction, commercial
    status = db.Column(db.String(20), default='active')  # active, archived, sold
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Financial inputs stored as JSON
    inputs = db.Column(db.Text, nullable=True)  # JSON
    outputs = db.Column(db.Text, nullable=True)  # JSON

    # Relationships
    scenarios = db.relationship('DealScenario', backref='deal', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='deal', lazy='dynamic')

    def __repr__(self):
        return f'<Deal {self.name}>'


class DealScenario(db.Model):
    __tablename__ = 'deal_scenarios'

    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    inputs = db.Column(db.Text, nullable=True)  # JSON
    outputs = db.Column(db.Text, nullable=True)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# CONSTRUCTION COST CALCULATOR
# ─────────────────────────────────────────

class ConstructionProject(db.Model):
    __tablename__ = 'construction_projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    province_state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(10), default='CA')
    postal_zip = db.Column(db.String(20), nullable=True)
    building_type = db.Column(db.String(50), nullable=False)  # sfh, duplex, townhouse, multi_family, commercial, mixed_use
    stories = db.Column(db.Integer, default=1)
    floor_area_sqft = db.Column(db.Float, nullable=False)
    foundation_type = db.Column(db.String(30), nullable=False)  # slab, basement, crawl
    construction_type = db.Column(db.String(30), nullable=False)  # wood_frame, concrete_block, steel_frame
    finish_level = db.Column(db.String(20), nullable=False)  # basic, standard, premium, luxury
    start_date = db.Column(db.Date, nullable=True)
    unit_system = db.Column(db.String(10), default='imperial')  # imperial, metric
    contingency_pct = db.Column(db.Float, default=10.0)
    status = db.Column(db.String(20), default='active')
    share_token = db.Column(db.String(64), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bom_items = db.relationship('BOMItem', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    permit_items = db.relationship('PermitItem', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    scenarios = db.relationship('ConstructionScenario', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('ConstructionAuditLog', backref='project', lazy='dynamic', cascade='all, delete-orphan')


class BOMItem(db.Model):
    __tablename__ = 'bom_items'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('construction_projects.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    is_custom = db.Column(db.Boolean, default=False)
    is_overridden = db.Column(db.Boolean, default=False)
    original_unit_cost = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    @property
    def line_total(self):
        return self.quantity * self.unit_cost


class PermitItem(db.Model):
    __tablename__ = 'permit_items'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('construction_projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    estimated_fee = db.Column(db.Float, default=0.0)
    processing_time = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_required = db.Column(db.Boolean, default=True)
    is_overridden = db.Column(db.Boolean, default=False)


class ConstructionScenario(db.Model):
    __tablename__ = 'construction_scenarios'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('construction_projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    inputs_snapshot = db.Column(db.Text, nullable=True)  # JSON
    overrides_snapshot = db.Column(db.Text, nullable=True)  # JSON
    total_cost = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ConstructionAuditLog(db.Model):
    __tablename__ = 'construction_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('construction_projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# REGIONAL COST DATA
# ─────────────────────────────────────────

class CityData(db.Model):
    __tablename__ = 'city_data'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    province_state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(10), nullable=False)
    land_cost_sqft = db.Column(db.Float, default=0.0)
    labor_index = db.Column(db.Float, default=1.0)
    material_index = db.Column(db.Float, default=1.0)
    permit_base_fee = db.Column(db.Float, default=0.0)
    cost_sfh_basic = db.Column(db.Float, default=0.0)
    cost_sfh_standard = db.Column(db.Float, default=0.0)
    cost_sfh_premium = db.Column(db.Float, default=0.0)
    cost_sfh_luxury = db.Column(db.Float, default=0.0)
    cost_multi_basic = db.Column(db.Float, default=0.0)
    cost_multi_standard = db.Column(db.Float, default=0.0)
    cost_multi_premium = db.Column(db.Float, default=0.0)
    cost_commercial_standard = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CityData {self.city}, {self.province_state}>'


# ─────────────────────────────────────────
# PROJECT MANAGEMENT
# ─────────────────────────────────────────

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='active')  # active, completed, on_hold
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    total_budget = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    budget_items = db.relationship('BudgetLineItem', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    draw_requests = db.relationship('DrawRequest', backref='project', lazy='dynamic', cascade='all, delete-orphan')


class BudgetLineItem(db.Model):
    __tablename__ = 'budget_line_items'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    trade = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    budgeted_amount = db.Column(db.Float, default=0.0)
    bid_amount = db.Column(db.Float, nullable=True)
    awarded_amount = db.Column(db.Float, nullable=True)
    actual_amount = db.Column(db.Float, default=0.0)
    contractor = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(30), default='pending')

    @property
    def variance(self):
        return self.actual_amount - (self.awarded_amount or self.budgeted_amount)


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    budget_item_id = db.Column(db.Integer, db.ForeignKey('budget_line_items.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # income, expense
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    trade = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=False)
    receipt_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DrawRequest(db.Model):
    __tablename__ = 'draw_requests'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    draw_number = db.Column(db.Integer, nullable=False)
    amount_requested = db.Column(db.Float, nullable=False)
    amount_approved = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    submitted_date = db.Column(db.Date, nullable=True)
    approved_date = db.Column(db.Date, nullable=True)
    lender_name = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# DOCUMENT MANAGEMENT
# ─────────────────────────────────────────

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    folder = db.Column(db.String(50), default='general')  # contracts, permits, drawings, invoices, correspondence, photos
    tags = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    share_token = db.Column(db.String(64), unique=True, nullable=True)
    share_expiry = db.Column(db.DateTime, nullable=True)
    share_password = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# CRM — BUYERS & LENDERS
# ─────────────────────────────────────────

class BuyerContact(db.Model):
    __tablename__ = 'buyer_contacts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    investor_type = db.Column(db.String(50), nullable=True)  # cash_buyer, landlord, developer, flipper
    buying_criteria = db.Column(db.Text, nullable=True)
    target_areas = db.Column(db.String(255), nullable=True)
    max_price = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LenderContact(db.Model):
    __tablename__ = 'lender_contacts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    loan_type = db.Column(db.String(50), nullable=True)  # private, hard_money, bridge, construction
    interest_rate = db.Column(db.Float, nullable=True)
    max_ltv = db.Column(db.Float, nullable=True)
    min_loan = db.Column(db.Float, nullable=True)
    max_loan = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(30), default='active')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# NOTIFICATIONS & ACTIVITY
# ─────────────────────────────────────────

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default='info')  # info, warning, success, error
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)  # deal, project, document, construction
    entity_id = db.Column(db.Integer, nullable=True)
    entity_name = db.Column(db.String(200), nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)