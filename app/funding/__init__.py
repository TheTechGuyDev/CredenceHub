from flask import Blueprint

funding = Blueprint('funding', __name__)

from app.funding import routes