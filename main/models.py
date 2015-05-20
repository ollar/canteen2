from main.database import Base
from flask.ext.login import UserMixin

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from werkzeug import generate_password_hash
from werkzeug.security import gen_salt
import datetime

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    real_name = Column(String)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    timestamp_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    timestamp_modified = Column(DateTime)

    def __init__(self, username, password, real_name=""):
        self.real_name = real_name
        self.username = username
        self.password = generate_password_hash(str(password).encode())
        self.timestamp_modified = datetime.datetime.utcnow()

    def __repr__(self):
        return '<User {0}>'.format(self.username)


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    order_date = Column(Date)
    meal_id = Column(Integer, ForeignKey('meal.id', ondelete='CASCADE'))
    quantity = Column(Integer, default=1, nullable=False)
    timestamp_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    timestamp_modified = Column(DateTime)

    user = relationship('User')
    meal = relationship('Meal')

    def __init__(self, order_date, meal_id, user_id, quantity):
        self.user_id = user_id
        self.order_date = order_date
        self.meal_id = meal_id
        self.quantity = quantity
        self.timestamp_modified = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Order: {0} by {1}>'.format(self.order_date, self.user_id)


class Meal(Base):
    __tablename__ = 'meal'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    category = Column(Integer)
    day_linked = Column(Integer)
    enabled = Column(Boolean, default=True)
    timestamp_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    timestamp_modified = Column(DateTime)

    def __init__(self, title, description, category, day_linked, enabled=1, *args, **kwargs):
        self.title = title
        self.description = description
        self.category = category
        self.day_linked = day_linked
        self.enabled = enabled
        self.timestamp_modified = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Meals {0}>'.format(self.title)


class Token(Base):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    token = Column(String(40))
    expires = Column(DateTime)

    def __init__(self, user_id):
        self.user_id = user_id
        self.token = self.generate_token()
        self.expires = self.calc_expire_date()

    @staticmethod
    def generate_token():
        return gen_salt(40)

    @staticmethod
    def calc_expire_date():
        _date = datetime.datetime.utcnow() + datetime.timedelta(3)

        return _date

    def is_expired(self):
        return self.expires < datetime.datetime.utcnow()

    def __repr__(self):
        return "<Token {0} for user {1}>".format(self.id, self.user_id)
