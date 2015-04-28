from flask import Blueprint, jsonify, request, abort, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from main.database import db_session, Meal
from main.functions import register_api
import datetime
import json

bp_meal = Blueprint('bp_meal', __name__, url_prefix='/meal')

class MealAPI(MethodView):
    def __init__(self):
        self.json = request.json

    def _parse_meal(self, meal_obj):
        meal = {
            'id': meal_obj.id,
            'title': meal_obj.title,
            'description': meal_obj.description,
            'category': meal_obj.category,
            'day_linked': meal_obj.day_linked,
            'enabled': meal_obj.enabled,
            'timestamp_created': meal_obj.timestamp_created,
            'timestamp_modified': meal_obj.timestamp_modified
        }

        return meal

    def get(self, meal_id):
        if meal_id:
            meal = db_session.query(Meal).get(meal_id)
            if meal:
                return jsonify(self._parse_meal(meal))
            else:
                return make_response(jsonify({'error': 'not found'}), 404)

        meals = db_session.query(Meal).all()
        meals[:] = [self._parse_meal(meal) for meal in meals]
        return jsonify({'meals': meals})
    #
    def post(self):
        new_meal = Meal(title=self.json.get('title'),
                        description=self.json.get('description'),
                        category=self.json.get('category'),
                        day_linked=self.json.get('day_linked'),
                        enabled=self.json.get('enabled'),
                        timestamp_modified=datetime.datetime.utcnow())

        db_session.add(new_meal)
        db_session.commit()

        return jsonify(self._parse_meal(new_meal))

    def put(self, meal_id):
        json_dict = {
            'title': self.json.get('title'),
            'description': self.json.get('description'),
            'category': self.json.get('category'),
            'day_linked': self.json.get('day_linked'),
            'enabled': self.json.get('enabled')
        }

        json_dict.update({'timestamp_modified': datetime.datetime.utcnow()})

        update_meal = db_session.query(Meal).filter_by(id=meal_id)
        update_meal.update(json_dict)

        db_session.commit()

        return jsonify(self._parse_meal(update_meal.first()))

    def delete(self, meal_id):
        meal = db_session.query(Meal).get(meal_id)
        if meal:
            db_session.delete(meal)
            db_session.commit()
            return jsonify(self._parse_meal(meal))
        return make_response(jsonify({'error': 'not found'}), 404)

register_api(MealAPI, 'meal_api', '/meal/', pk='meal_id')
