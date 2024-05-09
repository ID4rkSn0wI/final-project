import datetime
import json
import os

from flask import render_template, redirect, abort, request, make_response, jsonify
# from wtforms import
from flask_login import login_user, login_required, logout_user, current_user
from wtforms.fields.simple import SubmitField

from data import db_session
from data.forms import RegisterForm, LoginForm, SearchForm, MessageForm, FiltersForm
from data.messages import Message
from data.users import User, Chat
from utils.static_functions import get_img, set_filters

from setup import logger, app, login_manager


@logger.catch
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@logger.catch
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@logger.catch
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    form.sex.data = 'Мужской'
    form.school.data = 'Школа №67'
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            sex=form.sex.data,
            school=form.school.data,
            about=form.about.data,
            tags=', '.join(form.tags.data)
        )
        if form.photo.data:
            user.img_src = f'static/img/{user.id}.{form.photo.data.filename.split(".")[-1]}'
            with open(f'static/img/{user.id}.{form.photo.data.filename.split(".")[-1]}', 'wb') as f:
                f.write(form.photo.data.read())
        else:
            user.img_src = f"static/img/def.png"
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form)


@logger.catch
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@logger.catch
@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html', title='Профиль')


@logger.catch
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit():
    form = RegisterForm()
    form.submit.label.text = 'Сохранить'
    if request.method == "GET":
        if current_user.is_authenticated:
            form.name.data = current_user.name
            form.surname.data = current_user.surname
            form.age.data = current_user.age
            form.email.data = current_user.email
            form.sex.data = current_user.sex
            form.tags.data = current_user.tags.split(', ')
            form.about.data = current_user.about
            form.school.data = current_user.school
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data, User.email != current_user.email).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = db_sess.query(User).get(current_user.id)
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.age = form.age.data
        user.about = form.about.data
        user.sex = form.sex.data
        user.school = form.school.data
        user.tags = ', '.join(form.tags.data)
        if form.photo.data:
            user.img_src = f'static/img/{user.id}.{form.photo.data.filename.split(".")[-1]}'
            with open(f'static/img/{user.id}.{form.photo.data.filename.split(".")[-1]}', 'wb') as f:
                f.write(form.photo.data.read())
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/profile')
    return render_template('edit_profile.html', title='Редактирование', form=form)


@logger.catch
@app.route('/delete_cur_user')
def delete_cur_user():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        db_sess.delete(user)
        db_sess.commit()
        logout()
        return redirect('/')


@logger.catch
@app.route('/profile/<int:idd>')
def user_profile(idd):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(idd)
        return render_template('person_profile.html', title=f'{user.surname} {user.name}', user=user,
                               like=False)
    return redirect('/login')


@logger.catch
@app.route('/like/<int:idd>')
def like_profile(idd):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(idd)
        db_sess.close()
        img_src = get_img(user)
        return render_template('person_profile.html', title=f'{user.surname} {user.name}', user=user,
                               img_src=img_src, like=True)
    return redirect('/login')


@logger.catch
@app.route('/unlike/<int:idd>')
def unlike_profile(idd):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(idd)
        db_sess.close()
        img_src = get_img(user)
        return render_template('person_profile.html', title=f'{user.surname} {user.name}', user=user,
                               img_src=img_src, like=False)
    return redirect('/login')


@logger.catch
@app.route('/message/<int:user_id>', methods=['GET', 'POST'])
def message(user_id):
    form = MessageForm()
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user_to = db_sess.query(User).filter(User.id == user_id).first()
        if not db_sess.query(Chat).filter(Chat.chat_participates.contains(current_user), Chat.chat_participates.contains(user_to)).all():
            chat = Chat()
            chat.chat_participates.append(current_user)
            chat.chat_participates.append(user_to)
            db_sess.add(chat)
            db_sess.commit()
        chats = db_sess.query(Chat).filter(Chat.chat_participates.contains(current_user)).all()
        return render_template('message.html', title=f'Сообщения', chats=chats, form=form, cur=user_id)
    return redirect('/login')


@logger.catch
@app.route('/send_message/<int:user_id>', methods=['POST'])
def send_message(user_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user_to = db_sess.query(User).filter(User.id == user_id).first()
        chat = db_sess.query(Chat).filter(Chat.chat_participates.contains(current_user), Chat.chat_participates.contains(user_to)).first()
        message = Message()
        message.text = request.form['text']
        message.from_who_id = current_user.id
        message.chat = chat
        message.date = datetime.datetime.now().strftime("%H:%M:%S")
        db_sess.add(message)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/message/{user_id}')
    return redirect('/login')


@logger.catch
@app.route('/messages')
def messages():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        chats = db_sess.query(Chat).filter(Chat.chat_participates.contains(current_user)).all()
        return render_template('messages.html', title=f'Сообщения', chats=chats)
    return redirect('/login')


@logger.catch
@app.route('/feed', methods=['GET', 'POST'])
def feed():
    form = SearchForm()
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        if request.method == 'POST' and form.validate_on_submit():
            if form.query.data:
                users = db_sess.query(User).filter(User.name.like(f"%{form.query.data}%") | User.surname.like(f"%{form.query.data}%"))
            else:
                users = db_sess.query(User)
            users = set_filters(users.filter(User.id != current_user.id), current_user.id).all()
            return render_template('feed.html', title=f'Лента', users=users, form=form)
        users = db_sess.query(User).filter(User.id != current_user.id).all()
        return render_template('feed.html', title=f'Лента', form=form, users=users)
    return redirect('/login')


@logger.catch
@app.route('/followed')
def followed():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        users = current_user.followed
        return render_template('followed.html', title=f'Уведомления', users=users)
    return redirect('/login')


@logger.catch
@app.route('/followers')
def followers():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        users = current_user.followers
        return render_template('followers.html', title=f'Подписчики', users=users)
    return redirect('/login')


@logger.catch
@app.route('/filters', methods=['GET', 'POST'])
def filters():
    form = FiltersForm()
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        if request.method == 'POST' and form.validate_on_submit():
            user_filters = {
                'age_from': form.age_from.data,
                'age_to': form.age_to.data,
                'school': form.school.data,
                'tags': form.tags.data
            }
            with open('filter_settings.json', 'r') as f:
                all_filter = json.load(f)
            with open('filter_settings.json', 'w') as f:
                all_filter[str(current_user.id)] = user_filters
                f.write(json.dumps(all_filter, ensure_ascii=False, indent=4))
            return redirect('/feed')
        return render_template('filters.html', title=f'Фильтры', form=form)
    return redirect('/login')


@logger.catch
@app.route('/')
def main():
    return render_template('base.html', title='Main')
