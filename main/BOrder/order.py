from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from main.database import db_session
from main.models import Order
from main.functions import register_api, _parse_order, auth_required, user_allowed
import datetime
import json

bp_order = Blueprint('bp_order', __name__, url_prefix='/order')

class Order_API(MethodView):
    def __init__(self):
        self.json = request.json

    def _check_order(self):
        _order = db_session.query(Order).filter_by(meal_id=self.json.get('meal_id'), order_date=self.json.get('order_date')).all()

        if _order:
            return False
        else:
            return True

    @auth_required
    def get(self, order_id):
        if order_id:
            order = db_session.query(Order).get(order_id)
            if order:
                return jsonify(_parse_order(order))
            else:
                return make_response(jsonify({'error': 'not found'}), 404)

        orders = db_session.query(Order).all()
        if orders:
            orders[:] = [_parse_order(order) for order in orders]
        return jsonify({'orders': orders})

    @auth_required
    def post(self):
        if not self._check_order():
            return make_response(jsonify({'error': 'already ordered'}), 400)

        new_order = Order(order_date=datetime.datetime.strptime(self.json.get('order_date'), "%Y-%m-%d").date(),
                        meal_id=self.json.get('meal_id'),
                        user_id=self.json.get('user_id'),
                        quantity=self.json.get('quantity'))

        db_session.add(new_order)
        db_session.commit()

        return jsonify(_parse_order(new_order))

    @auth_required
    def put(self, order_id):
        pass

    @auth_required
    def delete(self, order_id):
        order = db_session.query(Order).get(order_id)
        if order:
            db_session.delete(order)
            db_session.commit()
            return jsonify({'status': 'success'})
        return make_response(jsonify({'error': 'not found'}), 404)

register_api(Order_API, 'order_api', '/order/', pk='order_id')
