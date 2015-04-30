from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from main.database import db_session, Order
from main.functions import register_api, _parse_order
import datetime
import json

bp_order = Blueprint('bp_order', __name__, url_prefix='/order')

class Order_API(MethodView):
    def __init__(self):
        self.json = request.json

    def get(self, order_id):
        if order_id:
            order = db_session.query(Order).get(order_id)
            if order:
                return jsonify(_parse_order(order))
            else:
                return make_response(jsonify({'error': 'not found'}), 404)

        orders = db_session.query(Order).all()
        orders[:] = [_parse_order(order) for order in orders]
        return jsonify({'orders': orders})

    def post(self):
        print(self.json)
        new_order = Order(order_date=datetime.datetime.strptime(self.json.get('order_date'), "%Y-%m-%d").date(),
                        meal_id=self.json.get('meal_id'),
                        user_id=self.json.get('user_id'),
                        quantity=self.json.get('quantity'))

        db_session.add(new_order)
        db_session.commit()

        return jsonify(_parse_order(new_order))

    def put(self, order_id):
        pass

    def delete(self, order_id):
        order = db_session.query(Order).get(order_id)
        if order:
            db_session.delete(order)
            db_session.commit()
            return jsonify(_parse_order(order))
        return make_response(jsonify({'error': 'not found'}), 404)

register_api(Order_API, 'order_api', '/order/', pk='order_id')
