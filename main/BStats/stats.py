from flask import Blueprint, jsonify, request, abort, make_response, g
from flask.views import MethodView, View
from sqlalchemy.exc import IntegrityError
from main.database import db_session
from main.models import Order
from main.functions import _parse_order, auth_required, restrict_users
import datetime
import calendar


bp_stats = Blueprint('bp_stats', __name__, url_prefix='/stats')


class MonthStats(View):

    def __init__(self):
        self.today = datetime.date.today()
        self.this_month = self.today.month

        if hasattr(g.user, 'id'):
            self.head_user_id = g.user.id
        else:
            self.head_user_id = None

        self.user_id = request.args.get('user_id')
        if request.args.get('month_number'):
            self.month_number = int( request.args.get('month_number') )
        else:
            self.month_number = None

    def _get_month_length(self, month_number):
        return calendar.monthrange(self.today.year, month_number)[1]

    def _get_month_dates(self, _month_number):
        return map(lambda day: datetime.date(self.today.year, _month_number, day), range(1, self._get_month_length(_month_number) + 1))

    @auth_required
    def dispatch_request(self):
        if int(self.user_id) != self.head_user_id and self.head_user_id != 1:
            return make_response(jsonify({'type': 'error', 'text': 'Access denied'}), 403)
        _month_number = self.month_number
        if not self.month_number:
            _month_number = self.this_month

        if self.user_id:
            orders = list(map(lambda day: db_session.query(Order).filter_by(
                order_date=day, user_id=self.user_id).all(), self._get_month_dates(_month_number)))
        else:
            if self.head_user_id == 1:
                orders = list(map(lambda day: db_session.query(Order).filter_by(
                    order_date=day).all(), self._get_month_dates(_month_number)))
            else:
                orders = list(map(lambda day: db_session.query(Order).filter_by(
                    order_date=day, user_id=self.head_user_id).all(), self._get_month_dates(_month_number)))



        orders[:] = [_parse_order(_order)
                     for _day_orders in orders for _order in _day_orders]
        return jsonify({'orders': orders})


class WeekMenu(View):

    def __init__(self):
        self.today = datetime.date.today() + datetime.timedelta(days=7)
        if hasattr(g.user, 'id'):
            self.head_user_id = g.user.id
        else:
            self.head_user_id = None
        self.user_id = request.args.get('user_id')
        if self.user_id:
            self.user_id = int(self.user_id)

    def _get_week_dates(self):
        return map(lambda day: self.today + datetime.timedelta(days=(day - self.today.weekday())), range(0, 5))

    @auth_required
    def dispatch_request(self):
        if self.user_id != self.head_user_id and self.head_user_id != 1:
            return make_response(jsonify({'type': 'error', 'text': 'Access denied'}), 403)
        if self.user_id:
            orders = list(map(lambda day: db_session.query(Order).filter_by(
                order_date=day, user_id=self.user_id).all(), self._get_week_dates()))
        else:
            if self.head_user_id == 1:
                orders = list(map(lambda day: db_session.query(Order).filter_by(
                    order_date=day).all(), self._get_week_dates()))
            else:
                orders = list(map(lambda day: db_session.query(Order).filter_by(
                    order_date=day, user_id=self.head_user_id).all(), self._get_week_dates()))

        orders[:] = [_parse_order(_order)
                     for _day_orders in orders for _order in _day_orders]
        return jsonify({'orders': orders})


month_stats = MonthStats.as_view('month_stats')
bp_stats.add_url_rule('/month', view_func=month_stats)

week_menu = WeekMenu.as_view('week_menu')
bp_stats.add_url_rule('/week', view_func=week_menu)
