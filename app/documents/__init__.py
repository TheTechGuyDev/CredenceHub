from flask import Blueprint

documents = Blueprint('documents', __name__)

from app.documents import routes