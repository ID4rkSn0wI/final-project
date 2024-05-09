import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, ForeignKey, Integer, Column, String, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


followers = Table('followers', SqlAlchemyBase.metadata,
            Column('follower_id', Integer, ForeignKey('users.id')),
            Column('followed_id', Integer, ForeignKey('users.id'))
            )


chats = Table('chats', SqlAlchemyBase.metadata,
            Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
            Column('chat_id', Integer, ForeignKey('chat.id'), primary_key=True)
            )


class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_participates = orm.relationship('User', secondary=chats, back_populates="in_chats")
    messages = orm.relationship('Message', back_populates='chat')

    def __repr__(self):
        return f"<Chat> {self.id} {self.chat_participates} {self.messages}"


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    about = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=False)
    sex = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    img_src = Column(String, nullable=False)
    school = Column(String, nullable=False)
    followed = relationship('User',
                            secondary=followers,
                            primaryjoin=(followers.c.follower_id == id),
                            secondaryjoin=(followers.c.followed_id == id),
                            backref=backref('followers'))
    in_chats = orm.relationship('Chat', secondary=chats, back_populates="chat_participates")
    hashed_password = Column(String, nullable=True)

    def __repr__(self):
        return f"<User> {self.id} {self.surname} {self.name}"

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return user in self.followed

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)