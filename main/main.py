from flask import Flask, jsonify, request
from flask.views import MethodView

import datetime
import sys

DEBUG = False
if len(sys.argv) > 1 and sys.argv[1] == '-d':
    DEBUG = True

app = Flask(__name__)

# ==============================================================================
# ==================================================================== ##Configs
# ==============================================================================

if DEBUG:
    from main.Flask_configs import DevConfig as flask_configs
else:
    from main.Flask_configs import Config as flask_configs

app.config.from_object(flask_configs)

from main.database import db_session

# ==============================================================================
# ==============================================================================
# ==============================================================================

import flask.ext.login as flask_login

login_manager = flask_login.LoginManager()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# ==============================================================================
# ======================================================================= ##User
# ==============================================================================

from main.BUser.user import bp_user
app.register_blueprint(bp_user)
