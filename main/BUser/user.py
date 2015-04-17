from flask import Blueprint, jsonify, request
from flask.views import MethodView
from main.database import db_session, User
import datetime

bp_user = Blueprint('bp_user', __name__, url_prefix='/user')

class UserView(MethodView):
    def __init__(self):
        pass

    def get(self):
        return jsonify({'page':'user', 'method': request.method})
    #
    def post(self):
        return jsonify({'page':'user', 'method': request.method})

    def put(self):
        return jsonify({'page':'user', 'method': request.method})

    def delete(self):
        return jsonify({'page':'user', 'method': request.method})



bp_user.add_url_rule('/', view_func=UserView.as_view('user_view'))
