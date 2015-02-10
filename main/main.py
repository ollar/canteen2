from flask import Flask



app = Flask(__name__)


# --------------------------------------------------------------------
# ------------------------------------------------------------ Configs
# --------------------------------------------------------------------

# from main.Flask_configs import Config as flask_configs

# app.config.from_object(flask_configs)

# from main.local_configs import LocalConfigs as local_configs

# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------

import flask.ext.login as flask_login

login_manager = flask_login.LoginManager()
login_manager.login_view = 'bp_user.user_login'
login_manager.login_message_category = 'notice'






from main.database import db_session

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()