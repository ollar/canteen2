from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from main.database import Base
from main.main import flask_login
import datetime

class User(Base, flask_login.UserMixin):
    __tablename__ = 'user'
    __table_args__ = {"useexisting": True}
    id = Column(Integer, primary_key=True)
    real_name = Column(String)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    timestamp_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    date_modified = Column(Date)

    def __init__(self, username, password, real_name=""):
        self.real_name = real_name
        self.username = username
        self.password = generate_password_hash(password)

    def __repr__(self):
        return '<User {0}>'.format(self.username)


class Order(Base):
    __tablename__ = 'order'
    __table_args__ = {"useexisting": True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    timestamp_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    order_date = Column(Date)
    meal_id = Column(Integer, ForeignKey('meal.id'))
    quantity = Column(Integer, default=1, nullable=False)

    user = relationship('User')
    meal = relationship('Meal')

    def __init__(self, order_date, meal_id, user_id, quantity):
        self.user_id = user_id
        self.order_date = order_date
        self.meal_id = meal_id
        self.quantity = quantity

    def __repr__(self):
        return '<Order: {0} by {1}>'.format(self.date, self.user_id)


class Meal(Base):
    __tablename__ = 'meal'
    __table_args__ = {"useexisting": True}
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    timestamp_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    category = Column(Integer)
    day_linked = Column(Integer)
    enabled = Column(Integer, default=1)

    def __init__(self, title, description, category, day_linked, *args, **kwargs):
        self.title = title
        self.description = description
        self.category = category
        self.day_linked = day_linked
        self.enabled = enabled

    def __repr__(self):
        return '<Meals {0}>'.format(self.title)
