from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, StatementError
from main.database import db_session
from main.models import User, Token
from werkzeug import generate_password_hash, check_password_hash
from main.functions import register_api, _parse_user, auth_required, restrict_users
import datetime

bp_user = Blueprint('bp_user', __name__, url_prefix='/user')


class UserAPI(MethodView):

    def __init__(self):
        self.json = request.json

    @auth_required
    @restrict_users
    def get(self, user_id):
        if user_id:
            user = db_session.query(User).get(user_id)
            if user:
                return jsonify(_parse_user(user))
            else:
                return make_response(jsonify({'type': 'error', 'text': 'not found'}), 404)

        users = db_session.query(User).all()
        users[:] = [_parse_user(user) for user in users]
        return jsonify({'users': users})

    def post(self):
        assert self.json.get('username'), 'username is required'
        assert self.json.get('password'), 'password is required'

        new_user = User(real_name=self.json.get('real_name').strip(),
                        username=self.json.get('username').strip(),
                        password=self.json.get('password').strip(),
                        email=self.json.get('email').strip().lower())

        db_session.add(new_user)
        try:
            db_session.commit()
        except IntegrityError as e:
            return make_response(jsonify({'type': 'error', 'text': 'username not unique'}), 403)

        return jsonify(_parse_user(new_user))

    @auth_required
    @restrict_users
    def put(self, user_id):
        json_dict = {
            'real_name': self.json.get('real_name'),
            'username': self.json.get('username'),
            'email': self.json.get('email')
        }

        if self.json.get('password'):
            json_dict.update(
                {'password': generate_password_hash(str(self.json.get('password')).encode())})

        update_user = db_session.query(User).filter_by(id=user_id)
        try:
            update_user.update(json_dict)
            db_session.commit()
        except StatementError:
            return make_response(jsonify({'type': 'error', 'text': 'database error'}), 500)

        return make_response(jsonify(_parse_user(update_user.first())), 200)

    @auth_required
    @restrict_users
    def delete(self, user_id):
        user = db_session.query(User).get(user_id)
        if user:
            db_session.delete(user)
            db_session.commit()
            return jsonify(_parse_user(user, detailed=False))
        return make_response(jsonify({'type': 'error', 'text': 'not found'}), 404)


@bp_user.route('/login', methods=['POST'])
def login():
    json = request.json
    user = db_session.query(User).filter_by(
        username=json.get('username').strip()).first()
    if not user:
        return make_response(jsonify({'type': 'error', 'text': 'no users with such username'}), 401)
    elif check_password_hash(user.password, json.get('password').strip()):
        token = {}
        tokens = db_session.query(Token).filter_by(user_id=user.id).all()
        is_expired_list = list(map(lambda t: t.is_expired(), tokens))
        all_expired = all(is_expired_list)

        if all_expired:
            token = Token(user_id=user.id)
            db_session.add(token)
            db_session.commit()
        else:
            token = [t for t in tokens if not t.is_expired()].pop()

        logged_user = _parse_user(user)
        logged_user.update({'token': token.token})

        return make_response(jsonify(logged_user), 200)
    else:
        return make_response(jsonify({'type': 'error', 'text': 'password incorrect'}), 401)


@bp_user.route('/logout')
def logout():
    return ''

register_api(UserAPI, 'user_api', '/user/', pk='user_id')
