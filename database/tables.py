from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    telegram_id = Column(Integer)
    birthday_date = Column(Date)

    def __repr__(self):
        return f'{self.id}. {self.user_name}'


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    birthday_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_status = Column(Boolean, default=False)
    summ = Column(Integer, default=0)
