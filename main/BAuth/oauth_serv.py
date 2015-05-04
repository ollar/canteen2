from main.main import app
from flask import Blueprint
from .models import Client, Grant, Token

bp_oauth = Blueprint('bp_oauth', __name__)
