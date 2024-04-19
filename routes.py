import os

from flask import render_template, redirect, abort, request, make_response, jsonify
# from wtforms import
from flask_login import login_user, login_required, logout_user, current_user

from data import db_session
from data.forms import RegisterForm, LoginForm
from data.users import User

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
            age=form.age.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        if form.photo:
            with open(f'static/img/{user.id}.{form.photo.data.filename.split(".")[-1]}', 'wb') as f:
                f.write(form.photo.data.read())
        redirect("/login")
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
    user = current_user
    name = user.name
    surname = user.surname
    age = user.age
    email = user.email
    password = user.hashed_password
    extensions = ['png', 'jpg', 'jpeg']
    img_src = 'static/img/def.png'
    if any([os.path.exists(f"static/img/{user.id}.{ext}") for ext in extensions]):
        img_src = list(filter(lambda y: os.path.exists(y), [f'static/img/{user.id}.{e}' for e in extensions]))[0]
    return render_template('profile.html', title='Профиль', name=name, surname=surname, age=age,
                           email=email, password=password, img_src=img_src)


@logger.catch
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit():
    form = RegisterForm()
    if request.method == "GET":
        if current_user.is_authenticated:
            form.name.data = current_user.name
            form.surname.data = current_user.surname
            form.age.data = current_user.age
            form.email.data = current_user.email
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
@app.route('/')
def main():
    return render_template('base.html', title='Main')


