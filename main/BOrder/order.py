from flask import Blueprint, jsonify, request, abort, make_response, g
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from main.database import db_session
from main.models import Order
from main.functions import register_api, _parse_order, auth_required, restrict_users
import datetime

bp_order = Blueprint('bp_order', __name__, url_prefix='/order')


class Order_API(MethodView):

    def __init__(self):
        self.json = request.json

    def _check_order(self):
        _orders = db_session.query(Order).filter_by(
            user_id=g.user.id,
            meal_id=self.json.get('meal_id'),
            order_date=self.json.get('order_date')
        ).all()

        if _orders:
            return False
        else:
            return True

    @staticmethod
    def _check_actual_date(check_date):
        """ Makes orders editable from today to two weeks further."""
        return check_date in range(datetime.date.today().timetuple().tm_yday, datetime.date.today().timetuple().tm_yday + 12)

    @auth_required
    @restrict_users
    def get(self, order_id):
        if order_id:
            order = db_session.query(Order).get(order_id)
            if order:
                return jsonify(_parse_order(order))
            else:
                return make_response(jsonify({'type': 'error', 'text': 'not found'}), 404)

        orders = db_session.query(Order).all()
        if orders:
            orders[:] = [_parse_order(order) for order in orders]
        return jsonify({'orders': orders})

    @auth_required
    def post(self):
        if not self._check_order():
            return make_response(jsonify({'type': 'error', 'text': 'This meal is already in your order'}), 403)

        _order_date = datetime.datetime.strptime(self.json.get('order_date'), "%Y-%m-%d").date()

        if not self._check_actual_date(_order_date.timetuple().tm_yday):
            return make_response(jsonify({'type': 'error', 'text': 'You are trying to create an outdated order. That is not allowed'}), 403)

        new_order = Order(order_date=_order_date,
                          meal_id=self.json.get('meal_id'),
                          user_id=self.json.get('user_id'),
                          quantity=self.json.get('quantity'))

        db_session.add(new_order)
        db_session.commit()

        return jsonify(_parse_order(new_order, detailed=False))

    @auth_required
    def delete(self, order_id):
        order = db_session.query(Order).get(order_id)

        if order:
            _order_date = order.order_date
            if not self._check_actual_date(_order_date.timetuple().tm_yday):
                return make_response(jsonify({'type': 'error', 'text': 'You are trying to remove old order. That is not allowed'}), 403)
            db_session.delete(order)
            db_session.commit()
            return jsonify({'status': 'success'})
        return make_response(jsonify({'type': 'error', 'text': 'not found'}), 404)

register_api(Order_API, 'order_api', '/order/', pk='order_id')
