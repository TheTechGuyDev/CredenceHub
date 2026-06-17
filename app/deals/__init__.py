from flask import Blueprint

deals = Blueprint('deals', __name__)

from app.deals import routes