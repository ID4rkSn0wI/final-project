import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, ForeignKey, Integer, Column, String, Table, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    chat = orm.relationship('Chat', back_populates='messages')
    from_who_id = Column(ForeignKey('users.id'))
    from_whom = orm.relationship("User")
    date = Column(String, default=datetime.datetime.now().strftime("%H:%M:%S"))
    # date = Column(DateTime, default=datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"))
    # to_who_id = Column(ForeignKey('users.id'))
    # to_whom = orm.relationship("User")
    text = Column(String, nullable=False)

    def __repr__(self):
        return f"<Message> {self.id} {self.text} {self.from_whom}"
