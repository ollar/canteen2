from main.main import app

def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

def _parse_user(user_obj, detailed=True):
    user = {
        'id': user_obj.id,
        'real_name': user_obj.real_name,
        'username': user_obj.username,
        # 'password': user_obj.password,
        'timestamp_created': str(user_obj.timestamp_created),
        'timestamp_modified': str(user_obj.timestamp_modified),
    }
    if detailed:
        user.update({'orders': [_parse_order(order, detailed=False) for order in user_obj.orders]})

    return user

def _parse_meal(meal_obj, *args, **kwargs):
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

    meal.update(kwargs)

    return meal

def _parse_order(order_obj, detailed=True):
    order = {
        'id': order_obj.id,
        'user_id': order_obj.user_id,
        'order_date': str(order_obj.order_date),
        'meal_id': order_obj.meal_id,
        'quantity': order_obj.quantity,
        'timestamp_created': str(order_obj.timestamp_created),
        'timestamp_modified': str(order_obj.timestamp_modified),
    }

    if detailed:
        order.update({
            'user': _parse_user(order_obj.user, detailed=False),
            'meal': _parse_meal(order_obj.meal)
        })
    return order
