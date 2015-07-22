from main.main import app
from flask import make_response, jsonify, g
from functools import wraps
import datetime

def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])


def _parse_user(user_obj, detailed=True):
    user = {
        'id': user_obj.id,
        'real_name': user_obj.real_name,
        'username': user_obj.username,
        'email': user_obj.email,
        # 'password': user_obj.password,
    }
    if detailed:
        user.update({
            'timestamp_created': str(user_obj.timestamp_created),
            'timestamp_modified': str(user_obj.timestamp_modified),
            'orders': [_parse_order(order, detailed=False) for (key, order) in enumerate(user_obj.orders) if key < 50],
            'comments': [_parse_comment(comment, detailed=False) for (key, comment) in enumerate(user_obj.comments) if key < 50]
        })

    return user


def _parse_meal(meal_obj, detailed=True, *args, **kwargs):
    this_month = datetime.datetime.today().month
    meal = {
        'id': meal_obj.id,
        'title': meal_obj.title,
        'category': meal_obj.category,
        'day_linked': meal_obj.day_linked,
        'source_price': meal_obj.source_price,
        'price': meal_obj.price,
    }

    if detailed:
        meal.update({
            'description': meal_obj.description,
            'enabled': meal_obj.enabled,
            'timestamp_created': meal_obj.timestamp_created,
            'timestamp_modified': meal_obj.timestamp_modified,
            'comments': [_parse_comment(comment, detailed=False) for comment in meal_obj.comments if comment.timestamp_modified.month == this_month]
        })

    meal.update(kwargs)

    return meal


def _parse_order(order_obj, detailed=True):
    order = {
        'id': order_obj.id,
        'user_id': order_obj.user_id,
        'order_date': str(order_obj.order_date),
        'meal_id': order_obj.meal_id,
        'quantity': order_obj.quantity,
    }

    if detailed:
        order.update({
            'timestamp_created': str(order_obj.timestamp_created),
            'timestamp_modified': str(order_obj.timestamp_modified),
            'user': _parse_user(order_obj.user, detailed=False),
            'meal': _parse_meal(order_obj.meal, detailed=False)
        })
    return order


def _parse_comment(comment_obj, detailed=True):
    comment = {
        'id': comment_obj.id,
        'user_id': comment_obj.user_id,
        'meal_id': comment_obj.meal_id,
        'content': comment_obj.content
    }

    if detailed:
        comment.update({
            'timestamp_created': str(comment_obj.timestamp_created),
            'timestamp_modified': str(comment_obj.timestamp_modified),
            'user': _parse_user(comment_obj.user, detailed=False),
            'meal': _parse_meal(comment_obj.meals, detailed=False)
        })

    return comment


def auth_required(f, *args, **kwargs):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user:
            return make_response(jsonify({'type': 'error', 'text': 'You need to log in for that'}), 401)
        return f(*args, **kwargs)
    return wrapper


def restrict_users(f):
    """
    Checks if logged user_id equals contents user_id.
    User can edit only his profile so urls /user/ are on scope. All other urls will allow only uid == 1.
    ex: /user/15 - content uid == 15, so only user with uid == 15 or 1 are allowed.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = kwargs.get('user_id', 0)

        if g.user and g.user.id in (1, user_id):
            return f(*args, **kwargs)
        else:
            return make_response(jsonify({'type': 'error', 'text': 'Access denied'}), 403)
    return wrapper
