from flask.ext.script import Manager, Command, Option
from main.main import app

from sqlalchemy import create_engine
from main.database import Base, db_session
from main.Flask_configs import Config, DevConfig
from main.models import User, Order, Meal
import random
import requests
import datetime
import json

manager = Manager(app)


class Hello(Command):
    """prints hello world"""

    def run(self):
        print("hello world")


class InitDB(Command):
    """
    Updates database with new models.
    """
    option_list = (
        Option('--debug', '-d', dest='debug', default=False),
    )

    def __init__(self):
        self.prod_sql_url, self.dev_sql_url = Config.SQLALCHEMY_DATABASE_URI, DevConfig.SQLALCHEMY_DATABASE_URI
        self.create_engine = create_engine
        self.Base = Base

    def run(self, debug):
        if debug:
            self.engine = self.create_engine(self.dev_sql_url, echo=True)
        else:
            self.engine = self.create_engine(self.prod_sql_url, echo=True)
        self.Base.metadata.drop_all(bind=self.engine)
        print("Database dropped.")
        self.Base.metadata.create_all(bind=self.engine)
        print("Database created.")


class PopulateMeals(Command):
    """
    Creates fake meals.
    """
    def __init__(self):
        pass

    def run(self):
        with open('./demo_meals.json', 'r') as f:
            meals = json.load(f)

            for meal in meals:
                new_meal = Meal(title=meal.get('title'),
                                description=meal.get('description'),
                                category=meal.get('category'),
                                day_linked=meal.get('day_linked'),
                                source_price=meal.get('source_price'),
                                price=meal.get('price'),
                                enabled=meal.get('enabled'),
                                timestamp_modified=datetime.datetime.utcnow())

                db_session.add(new_meal)
                print('Created meal:', new_meal)
            db_session.commit()


class PopulateUsers(Command):
    """
    Creates fake users.
    """
    option_list = (
        Option('--number', '-n', dest='num', default=20),
    )
    def __init__(self):
        pass

    def run(self, num):
        for i in range(num):
            with open('./words', 'r') as f:
                word = random.choice(f.read().splitlines())

            new_user = User(real_name=word,
                            username=word,
                            password=word)

            db_session.add(new_user)
            print('Created user:', new_user)
        db_session.commit()



class PopulateOrders(Command):
    """
    Creates fake orders.
    """
    option_list = (
        Option('--number', '-n', dest='num', default=200),
    )
    def __init__(self):
        self.users = db_session.query(User).all()
        self.meals = db_session.query(Meal).all()
        self.today = datetime.datetime.today()

    def _get_month_dates(self, num):
        start = datetime.date(self.today.year, self.today.month - 4, 1)

        for day in (start + datetime.timedelta(n) for n in range(num)):
            if day.weekday() in range(0,5):
                yield day


    def _get_day_meals(self, order_date):
        return [meal for meal in self.meals if meal.day_linked == order_date.weekday()]

    def run(self, num):
        for user in self.users:
            for date in self._get_month_dates(num):
                _meals = self._get_day_meals(date)

                for _m in _meals:
                    new_order = Order(order_date=date,
                                      meal_id=_m.id,
                                      user_id=user.id,
                                      quantity=random.randint(1,10))

                    db_session.add(new_order)
            print('Created order:', new_order)
        db_session.commit()
        print("Orders creation complete")


manager.add_command('hello', Hello)
manager.add_command('update_db', InitDB)
manager.add_command('popme', PopulateMeals)
manager.add_command('popus', PopulateUsers)
manager.add_command('popor', PopulateOrders)

if __name__ == '__main__':
    manager.run()
