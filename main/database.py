from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from main.main import app
engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import flask.ext.login as flask_login
from werkzeug import generate_password_hash
import datetime

class User(Base, flask_login.UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    real_name = Column(String)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    timestamp_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    timestamp_modified = Column(DateTime)

    def __init__(self, username, password, real_name="", timestamp_modified=""):
        self.real_name = real_name
        self.username = username
        self.password = generate_password_hash(str(password).encode())
        self.timestamp_modified = timestamp_modified

    def __repr__(self):
        return '<User {0}>'.format(self.username)


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    order_date = Column(Date)
    meal_id = Column(Integer, ForeignKey('meal.id'))
    quantity = Column(Integer, default=1, nullable=False)
    timestamp_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    timestamp_modified = Column(DateTime)

    # user = relationship('User')
    # meal = relationship('Meal')

    def __init__(self, order_date, meal_id, user_id, quantity):
        self.user_id = user_id
        self.order_date = order_date
        self.meal_id = meal_id
        self.quantity = quantity

    def __repr__(self):
        return '<Order: {0} by {1}>'.format(self.date, self.user_id)


class Meal(Base):
    __tablename__ = 'meal'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    category = Column(Integer)
    day_linked = Column(Integer)
    enabled = Column(Integer, default=1)
    timestamp_created = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    timestamp_modified = Column(DateTime)

    def __init__(self, title, description, category, day_linked, *args, **kwargs):
        self.title = title
        self.description = description
        self.category = category
        self.day_linked = day_linked
        self.enabled = enabled

    def __repr__(self):
        return '<Meals {0}>'.format(self.title)



def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
