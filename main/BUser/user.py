from flask import Blueprint, jsonify, request, abort, make_response, session
from flask.views import MethodView
from flask.ext.login import login_user, current_user, make_secure_token
from sqlalchemy.exc import IntegrityError, StatementError
from main.database import db_session
from main.models import User
from werkzeug import generate_password_hash, check_password_hash
from main.functions import register_api, _parse_user
import datetime
import json

bp_user = Blueprint('bp_user', __name__, url_prefix='/user')

class UserAPI(MethodView):
    def __init__(self):
        self.json = request.json

    def get(self, user_id):
        if user_id:
            user = db_session.query(User).get(user_id)
            if user:
                return jsonify(_parse_user(user))
            else:
                return make_response(jsonify({'error': 'not found'}), 404)

        users = db_session.query(User).all()
        users[:] = [_parse_user(user) for user in users]
        return jsonify({'users': users})

    def post(self):
        assert self.json.get('username'), 'username is required'
        assert self.json.get('password'), 'password is required'

        new_user = User(real_name=self.json.get('real_name'),
                        username=self.json.get('username'),
                        password=self.json.get('password'))


        db_session.add(new_user)
        try:
            db_session.commit()
        except IntegrityError as e:
            return make_response(jsonify({'error': 'username not unique'}), 500)

        login_user(new_user)
        print(session)

        return jsonify(_parse_user(new_user))

    def put(self, user_id):
        json_dict = self.json

        json_dict = {
            'real_name': self.json.get('real_name'),
            'username': self.json.get('username')
        }

        if json_dict.get('password'):
            json_dict.update({'password': generate_password_hash(str(json_dict.get('password')).encode())})

        json_dict['timestamp_modified'] = 'asdfasd'

        update_user = db_session.query(User).filter_by(id=user_id)
        try:
            update.update(json_dict)
            db_session.commit()
        except StatementError:
            return make_response(jsonify({'error': 'database error'}), 500)

        return make_response(jsonify(_parse_user(update_user.first())), 200)

    def delete(self, user_id):
        user = db_session.query(User).get(user_id)
        if user:
            db_session.delete(user)
            db_session.commit()
            return jsonify(_parse_user(user))
        return make_response(jsonify({'error': 'not found'}), 404)

@bp_user.route('/login', methods=['POST'])
def login():
    json = request.json
    user = db_session.query(User).filter_by(username=json.get('username')).first()
    if not user:
        return make_response(jsonify({'error': 'no users with such username'}), 401)
    elif check_password_hash(user.password, json.get('password')):
        return make_response(jsonify(_parse_user(user)), 200)
    else:
        return make_response(jsonify({'error': 'password incorrect'}), 401)

@bp_user.route('/logout')
def logout():
    flask_login.logout_user()
    return 'ok'


register_api(UserAPI, 'user_api', '/user/', pk='user_id')
