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

    def _get_month_length(self, month_number):
        return calendar.monthrange(self.today.year, month_number)[1]

    def _get_month_dates(self, _month_number):
        return map(lambda day: datetime.date(self.today.year, _month_number, day), range(1, self._get_month_length(_month_number) + 1))

    # @auth_required
    def dispatch_request(self, month_number=None, user_id=None):
        _month_number = month_number
        if not month_number:
            _month_number = self.this_month

        if user_id:
            orders = list(map(lambda day: db_session.query(Order).filter_by(
                order_date=day, user_id=user_id).all(), self._get_month_dates(_month_number)))
        else:
            orders = list(map(lambda day: db_session.query(Order).filter_by(
            order_date=day).all(), self._get_month_dates(_month_number)))

        orders[:] = [_parse_order(_order)
                     for _day_orders in orders for _order in _day_orders]
        return jsonify({'orders': orders})


class WeekMenu(View):

    def __init__(self):
        self.today = datetime.date.today() + datetime.timedelta(days=7)

    def _get_week_dates(self):
        return map(lambda day: self.today + datetime.timedelta(days=(day - self.today.weekday())), range(0, 5))

    # @auth_required
    def dispatch_request(self, user_id=None):
        if user_id:
                orders = list(map(lambda day: db_session.query(Order).filter_by(
                order_date=day, user_id=user_id).all(), self._get_week_dates()))
        else:
            orders = list(map(lambda day: db_session.query(Order).filter_by(
                order_date=day).all(), self._get_week_dates()))


        orders[:] = [_parse_order(_order)
                     for _day_orders in orders for _order in _day_orders]
        return jsonify({'orders': orders})


month_stats = MonthStats.as_view('month_stats')
bp_stats.add_url_rule('/month', view_func=month_stats)
bp_stats.add_url_rule('/month/<int:month_number>/<int:user_id>', view_func=month_stats)

week_menu = WeekMenu.as_view('week_menu')
bp_stats.add_url_rule('/week', view_func=week_menu)
bp_stats.add_url_rule('/week/<int:user_id>', view_func=week_menu)
