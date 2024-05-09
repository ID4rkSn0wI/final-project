from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import *
from wtforms.validators import DataRequired


CHOICES = [('Ищу парня/девушку', 'Ищу парня/девушку'), ('Ищу друга/подругу', 'Ищу друга/подругу'), ('Ищу с кем пообщаться', 'Ищу с кем пообщаться'), ('Ищу с кем поиграть', 'Ищу с кем поиграть')]
SCHOOLS = [('Школа №67', 'Школа №67')]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RegisterForm(FlaskForm):
    photo = FileField("Фото профиля", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    email = EmailField('Логин / email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    sex = RadioField('Пол', choices=[('Мужской', 'Мужской'), ('Женский', 'Женский')], validators=[DataRequired()])
    age = IntegerField("Возраст", validators=[DataRequired()])
    school = SelectField('Школа', choices=SCHOOLS, validators=[DataRequired()])
    about = StringField("О себе", validators=[DataRequired()])
    tags = MultiCheckboxField('Теги', choices=CHOICES)
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField('Войти')


class SearchForm(FlaskForm):
    query = StringField('Запрос')
    submit = SubmitField('Поиск')


class MessageForm(FlaskForm):
    text = StringField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class FiltersForm(FlaskForm):
    age_from = IntegerField("С какого возраста")
    age_to = IntegerField("До какого возраста")
    school = SelectField('Школа', choices=SCHOOLS)
    tags = MultiCheckboxField('Теги', choices=CHOICES)
    submit = SubmitField('Сохранить')