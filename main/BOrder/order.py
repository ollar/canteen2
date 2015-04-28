from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from main.database import db_session, Order
import datetime
import json

bp_order = Blueprint('bp_order', __name__, url_prefix='/order')

class Order_API(MethodView):
    def __init__(self):
        self.json = request.json

    def _parse_order(self, order_obj):
        order = {
            'id': order_obj.id,
            'user_id': order_obj.user_id,
            'order_date': str(order_obj.order_date),
            'meal_id': order_obj.meal_id,
            'quantity': order_obj.quantity,
            'timestamp_created': str(order_obj.timestamp_created),
            'timestamp_modified': str(order_obj.timestamp_modified)
        }
        return order

    def get(self, order_id):
        if order_id:
            order = db_session.query(Order).get(order_id)
            if order:
                return jsonify(self._parse_order(order))
            else:
                return make_response(jsonify({'error': 'not found'}), 404)

        orders = db_session.query(Order).all()
        orders[:] = [self._parse_order(order) for order in orders]
        return jsonify({'orders': orders})

    def post(self):
        new_order = Order(
                        # order_date=self.json.get('order_date'),
                        order_date=datetime.datetime.utcnow(),
                        meal_id=self.json.get('meal_id'),
                        user_id=self.json.get('user_id'),
                        quantity=self.json.get('quantity'),
                        timestamp_modified=datetime.datetime.utcnow())

        db_session.add(new_order)
        db_session.commit()

        return jsonify(self._parse_order(new_order))

    def put(self, order_id):
        pass

    def delete(self, order_id):
        order = db_session.query(Order).get(order_id)
        if order:
            db_session.delete(order)
            db_session.commit()
            return jsonify(self._parse_order(order))
        return make_response(jsonify({'error': 'not found'}), 404)

order_api = Order_API.as_view('index')
bp_order.add_url_rule('/', view_func=order_api, defaults={'order_id': None}, methods=['GET'])
bp_order.add_url_rule('/', view_func=order_api, methods=['POST'])
bp_order.add_url_rule('/<int:order_id>', view_func=order_api, methods=['GET', 'PUT', 'DELETE'])
