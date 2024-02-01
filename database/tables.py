from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    telegram_id = Column(Integer, index=True)
    birthday_date = Column(Date)

    events = relationship('Event', uselist=False, backref='user', cascade="all,delete")

    def __repr__(self):
        return f'{self.id}. {self.user_name}'


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    payers = relationship("Payer", backref="event", cascade="all,delete")

    def __repr__(self):
        return f'{self.id}. {self.user_id} {self.user.birthday_date}'


class Payer(Base):
    __tablename__ = "payers"

    id = Column(Integer, primary_key=True)
    payment_status = Column(Boolean, default=False)
    summ = Column(Integer, default=0)
    user_id = Column(Integer, nullable=False, unique=True)

    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)