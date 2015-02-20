from flask import Flask, jsonify, request
from flask.views import MethodView

import datetime

app = Flask(__name__)

# --------------------------------------------------------------------
# ------------------------------------------------------------ Configs
# --------------------------------------------------------------------

from main.Flask_configs import Config as flask_configs
app.config.from_object(flask_configs)

# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------

import flask.ext.login as flask_login

login_manager = flask_login.LoginManager()
login_manager.login_view = 'bp_user.user_login'
login_manager.login_message_category = 'notice'

from main.database import db_session, User

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()





class UserView(MethodView):
  def __init__(self):
    pass

  def get(self):
    users = db_session.query(User).all()
    print(users)
    return jsonify(users)

  def post(self):
    print(request.json)
    user_dict = {
      'real_name': request.json.get('real_name'),
      'username': request.json.get('username'),
      'password': request.json.get('password'),
      'timestamp_modified': datetime.datetime.utcnow()
    }

    _new_user = User(**user_dict)

    db_session.add(_new_user)
    db_session.commit()

    return jsonify({'status': 'ok'})



app.add_url_rule('/user', view_func=UserView.as_view('user_view'))