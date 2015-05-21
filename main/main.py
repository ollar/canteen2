from flask import Flask, jsonify, request, session
from flask.views import MethodView, View
from flask.ext.cors import CORS
import datetime
import sys

DEBUG = False
if len(sys.argv) > 1 and sys.argv[1] == '-d':
    DEBUG = True

app = Flask(__name__)
cors = CORS(app)

# ==============================================================================
# ==================================================================== ##Configs
# ==============================================================================

if DEBUG:
    from main.Flask_configs import DevConfig as flask_configs
else:
    from main.Flask_configs import Config as flask_configs

app.config.from_object(flask_configs)

from main.database import db_session
from main.models import Meal
from main.functions import _parse_meal

@app.before_request
def get_token():
    token = request.headers.get('access_token')
    session['access_token'] = token

# ==============================================================================
# ==============================================================================
# ==============================================================================

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# ==============================================================================
# ======================================================================= ##User
# ==============================================================================

from main.BUser.user import bp_user
app.register_blueprint(bp_user)


# ==============================================================================
# ======================================================================= ##Meal
# ==============================================================================

from main.BMeal.meal import bp_meal
app.register_blueprint(bp_meal)


# ==============================================================================
# ======================================================================= ##Meal
# ==============================================================================

from main.BOrder.order import bp_order
app.register_blueprint(bp_order)

# ==============================================================================
# ====================================================================== ##Views
# ==============================================================================

class NextWeekMenu(View):
    def __init__(self):
        self.today = datetime.date.today()
        self.next_week = self.today + datetime.timedelta(weeks=1)
        self.step = 0

    def run_week(self):
        while self.step < 5:
            day = self.next_week - datetime.timedelta(days=self.today.weekday() - self.step)
            meals = db_session.query(Meal).filter_by(day_linked=day.weekday(), enabled=True) \
                .order_by('category').all()

            yield meals, day
            self.step += 1

    def dispatch_request(self):
        meals = list(self.run_week())
        meals[:] = [_parse_meal(meal, order_date=str(date)) for day_meals, date in meals for meal in day_meals]
        return jsonify({'meals': meals})

home_page = NextWeekMenu.as_view('home')
app.add_url_rule('/', view_func=home_page)
