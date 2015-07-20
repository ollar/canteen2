from main.database import Base
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    meal_id = Column(Integer, ForeignKey('meal.id'))

    content = Column(String)

    timestamp_created = Column(
        DateTime, default=datetime.datetime.utcnow(), nullable=False)
    timestamp_modified = Column(DateTime)

    meals = relationship('Meal', backref='comments')
    user = relationship('User', backref='comments')

    def __init__(self, user_id, meal_id, content):
        self.user_id = user_id
        self.meal_id = meal_id
        self.content = content
        self.timestamp_modified = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Comment {0}>'.format(self.id)
