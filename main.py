from api import UsersListResource, UsersResource
from data import db_session
from setup import app, api
from routes import *

if __name__ == '__main__':
    db_session.global_init("db/users.db")
    api.add_resource(UsersListResource, '/api/v2/users')
    api.add_resource(UsersResource, '/api/v2/users/<int:user_id>')
    app.run(port=8080, host='127.0.0.1')