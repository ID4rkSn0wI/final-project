from flask import Blueprint, Flask, render_template, redirect, abort, request, make_response, jsonify
from wtforms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from loguru import logger
from flask_restful import reqparse, Api, Resource
from requests import get, post, delete


app = Flask(__name__)
blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


logger.add('debug.log', format='{time:YYYY-MM-DD at HH:mm:ss} | {name} : {function} : {line} | {message}',
           level='WARNING', rotation='1 day')
logger.add('catch.log', format='{time:YYYY-MM-DD at HH:mm:ss} | {name} : {function} : {line} | {message}',
           filter=lambda record: 'special' in record['extra'], rotation='1 day')
logger.add('info.log', format='{time:YYYY-MM-DD at HH:mm:ss} | {name} : {function} | {message}',
           level='INFO', rotation='1 day')
