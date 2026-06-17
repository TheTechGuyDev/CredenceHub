from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.auth import auth
from app.models import User, Profile


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.password_hash and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been suspended. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=bool(remember))
            user.last_login = db.func.now()
            db.session.commit()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if not user.onboarding_complete:
                return redirect(url_for('auth.onboarding'))
            
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', title='Login - CredenceHub')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validation
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        # Create user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            email=email,
            password_hash=password_hash,
            plan='lite'
        )
        db.session.add(user)
        db.session.flush()

        # Create profile
        profile = Profile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(profile)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Let\'s set up your profile.', 'success')
        return redirect(url_for('auth.onboarding'))

    return render_template('auth/register.html', title='Register - CredenceHub')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if current_user.onboarding_complete:
        return redirect(url_for('dashboard.index'))

    step = request.args.get('step', 1, type=int)

    if request.method == 'POST':
        step = request.form.get('step', 1, type=int)
        profile = current_user.profile

        if step == 1:
            profile.investor_role = request.form.get('investor_role')
            db.session.commit()
            return redirect(url_for('auth.onboarding', step=2))

        elif step == 2:
            profile.target_markets = request.form.get('target_markets')
            db.session.commit()
            return redirect(url_for('auth.onboarding', step=3))

        elif step == 3:
            profile.experience_level = request.form.get('experience_level')
            db.session.commit()
            return redirect(url_for('auth.onboarding', step=4))

        elif step == 4:
            profile.team_size = request.form.get('team_size')
            current_user.onboarding_complete = True
            db.session.commit()
            flash('Welcome to CredenceHub! Your account is ready.', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth/onboarding.html', title='Setup - CredenceHub', step=step)


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            flash('If that email exists in our system, a reset link has been sent.', 'info')
        else:
            flash('If that email exists in our system, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', title='Reset Password - CredenceHub')


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile

    if request.method == 'POST':
        profile.first_name = request.form.get('first_name', '').strip()
        profile.last_name = request.form.get('last_name', '').strip()
        profile.company_name = request.form.get('company_name', '').strip()
        profile.phone = request.form.get('phone', '').strip()
        profile.address = request.form.get('address', '').strip()
        profile.city = request.form.get('city', '').strip()
        profile.province_state = request.form.get('province_state', '').strip()
        profile.bio = request.form.get('bio', '').strip()
        profile.website = request.form.get('website', '').strip()
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', title='My Profile - CredenceHub', profile=profile)