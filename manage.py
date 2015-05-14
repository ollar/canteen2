from flask.ext.script import Manager, Command, Option
from main.main import app

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
        from sqlalchemy import create_engine
        from main.database import Base
        from main.Flask_configs import Config, DevConfig

        self.prod_sql_url, self.dev_sql_url = Config.SQLALCHEMY_DATABASE_URI, DevConfig.SQLALCHEMY_DATABASE_URI
        self.create_engine = create_engine
        self.Base = Base

    def run(self, debug):
        if debug:
            self.engine = self.create_engine(self.dev_sql_url)
        else:
            self.engine = self.create_engine(self.prod_sql_url)
        self.Base.metadata.drop_all(bind=self.engine)
        print("Database dropped.")
        self.Base.metadata.create_all(bind=self.engine)
        print("Database created.")


manager.add_command('hello', Hello())
manager.add_command('update_db', InitDB())

if __name__ == '__main__':
    manager.run()
