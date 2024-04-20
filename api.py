import flask_restful
from flask import jsonify, request
from flask_restful import reqparse
from setup import logger
from data import db_session
from data.users import User


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
                'name', 'surname', "age", 'about')))

    @logger.catch
    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('age', required=True, type=int)
parser.add_argument('about', required=True, type=int)
parser.add_argument('email', required=True, type=str)
parser.add_argument('hashed_password', required=True)


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
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            about=args['about'],
            email=args['email'],
        )
        user.set_password(request.json['hashed_password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})