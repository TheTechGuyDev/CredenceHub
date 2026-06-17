import os
from app import create_app, db
from app.models import User, Profile, Deal, ConstructionProject

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Profile': Profile,
        'Deal': Deal,
        'ConstructionProject': ConstructionProject
    }


@app.cli.command('init-db')
def init_db():
    """Initialize the database and create all tables."""
    with app.app_context():
        db.create_all()
        print('Database tables created successfully.')


@app.cli.command('seed-db')
def seed_db():
    """Seed the database with initial city cost data."""
    from app.utils.seed_data import seed_city_data
    with app.app_context():
        seed_city_data()
        print('City cost data seeded successfully.')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', '1') == '1'
    )