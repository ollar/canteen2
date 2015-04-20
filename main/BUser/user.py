from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from main.database import db_session, User
from werkzeug import generate_password_hash, check_password_hash
import datetime
import json

bp_user = Blueprint('bp_user', __name__, url_prefix='/user')

class UserAPI(MethodView):
    def __init__(self):
        self.json = request.json

    def _parse_user(self, user_obj):
        user = {
            'id': user_obj.id,
            'real_name': user_obj.real_name,
            'username': user_obj.username,
            'password': user_obj.password,
            'timestamp_created': str(user_obj.timestamp_created),
            'timestamp_modified': str(user_obj.timestamp_modified)
        }

        return user

    def get(self, user_id):
        if user_id:
            user = db_session.query(User).get(user_id)
            if user:
                return jsonify(self._parse_user(user))
            else:
                return make_response(jsonify({'error': 'not found'}), 404)

        users = db_session.query(User).all()
        users[:] = [self._parse_user(user) for user in users]
        return jsonify({'users': users})
    #
    def post(self):
        assert self.json.get('username'), 'username is required'
        assert self.json.get('password'), 'password is required'

        new_user = User(real_name=self.json.get('real_name'), username=self.json.get('username'), password=self.json.get('password'), timestamp_modified=datetime.datetime.utcnow())

        db_session.add(new_user)
        try:
            db_session.commit()
        except IntegrityError as e:
            return make_response(jsonify({'error': 'username not unique'}), 500)

        return jsonify(self._parse_user(new_user))

    def put(self, user_id):
        json_dict = {
            'username': self.json.get('username'),
            'real_name': self.json.get('real_name'),
            'timestamp_modified': datetime.datetime.utcnow()
        }

        if json_dict.get('password'):
            json_dict.update({'password': generate_password_hash(str(json_dict.get('password')).encode())})

        db_session.query(User).filter_by(id=user_id).update(json_dict)
        db_session.commit()

        return make_response(jsonify({'status':'ok'}), 200)

    def delete(self, user_id):
        user = db_session.query(User).get(user_id)
        if user:
            db_session.delete(user)
            db_session.commit()
            return jsonify({'status': 'ok'})
        return make_response(jsonify({'error': 'not found'}), 404)

user_api = UserAPI.as_view('index')
bp_user.add_url_rule('/', view_func=user_api, defaults={'user_id': None}, methods=['GET'])
bp_user.add_url_rule('/', view_func=user_api, methods=['POST'])
bp_user.add_url_rule('/<int:user_id>', view_func=user_api, methods=['GET', 'PUT', 'DELETE'])
