from flask import Blueprint

construction = Blueprint('construction', __name__)

from app.construction import routes