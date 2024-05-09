import datetime
import re

import flask_restful
from flask import jsonify, request
from flask_restful import reqparse

from data.messages import Message
from setup import logger
from data import db_session
from data.users import User, Chat

CHOICES = ['Ищу парня/девушку', 'Ищу друга/подругу', 'Ищу с кем пообщаться', 'Ищу с кем поиграть']
SCHOOLS = ['Школа №67']
SEX = ['Мужской', 'Женский']


@logger.catch
def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        flask_restful.abort(404, message=f"User {user_id} not found")


class UsersResource(flask_restful.Resource):
    @logger.catch
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify(users.to_dict(
            only=(
                'name',
                'surname',
                "age",
                'about'
            )))

    @logger.catch
    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True, type=str)
user_parser.add_argument('surname', required=True, type=str)
user_parser.add_argument('age', required=True, type=int)
user_parser.add_argument('about', required=True, type=int)
user_parser.add_argument('sex', required=True, type=str)
user_parser.add_argument('email', required=True, type=str)
user_parser.add_argument('school', required=True, type=str)
user_parser.add_argument('tags', required=True, type=str)
user_parser.add_argument('hashed_password', required=True)


class UsersListResource(flask_restful.Resource):
    @logger.catch
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'surname', "age", 'about'))
            for item in users]})

    @logger.catch
    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        if args['sex'] not in SEX:
            return jsonify({
                'result': False,
                'message': 'Bad Input'
                            })
        if args['school'] not in SCHOOLS:
            return jsonify({
                'result': False,
                'message': 'Bad Input'
                            })
        if not all([tag not in CHOICES for tag in args['tags'].split(', ')]):
            return jsonify({
                'result': False,
                'message': 'Bad Input'
                            })
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            sex=args['sex'],
            about=args['about'],
            email=args['email'],
            school=args['school'],
            tags=args['tags']
        )
        user.set_password(request.json['hashed_password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})


@logger.catch
def abort_if_chat_not_found(chat_id):
    session = db_session.create_session()
    user = session.query(Chat).get(chat_id)
    if not user:
        flask_restful.abort(404, message=f"Chat {chat_id} not found")


class ChatsResource(flask_restful.Resource):
    @logger.catch
    def get(self, chat_id):
        abort_if_users_not_found(chat_id)
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        return jsonify(chat.to_dict(
            only=(
                'chat_participates',
                'messages'
            )))

    @logger.catch
    def delete(self, chat_id):
        abort_if_users_not_found(chat_id)
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        session.delete(chat)
        session.commit()
        return jsonify({'success': 'OK'})


chat_parser = reqparse.RequestParser()


class ChatsListResource(flask_restful.Resource):
    @logger.catch
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=(
                'chat_participates',
                'messages'
            ))
            for item in users]})

    @logger.catch
    def post(self):
        args = chat_parser.parse_args()
        session = db_session.create_session()
        chat = Chat()
        session.add(chat)
        session.commit()
        return jsonify({'id': chat.id})


@logger.catch
def abort_if_message_not_found(message_id):
    session = db_session.create_session()
    user = session.query(Chat).get(message_id)
    if not user:
        flask_restful.abort(404, message=f"Message {message_id} not found")


class MessagesResource(flask_restful.Resource):
    @logger.catch
    def get(self, message_id):
        abort_if_users_not_found(message_id)
        session = db_session.create_session()
        message = session.query(Chat).get(message_id)
        return jsonify(message.to_dict(
            only=(
                'from_whom',
                'text',
                'date'
            )))

    @logger.catch
    def delete(self, message_id):
        abort_if_users_not_found(message_id)
        session = db_session.create_session()
        message = session.query(Chat).get(message_id)
        session.delete(message)
        session.commit()
        return jsonify({'success': 'OK'})


user_parser = reqparse.RequestParser()
user_parser.add_argument('text', required=True, type=str)
user_parser.add_argument('from_who_id', required=True, type=int)


class MessagesListResource(flask_restful.Resource):
    @logger.catch
    def get(self):
        session = db_session.create_session()
        messages = session.query(User).all()
        return jsonify({'messages': [item.to_dict(
            only=(
                'from_whom',
                'text',
                'date'
            ))
            for item in messages]})

    @logger.catch
    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        message = Message(
            from_who_id=args['from_who_id'],
            text=args['text'],
            date=datetime.datetime.now().strftime("%H:%M:%S")
        )
        session.add(message)
        session.commit()
        return jsonify({'id': message.id})