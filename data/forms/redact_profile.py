from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from flask_wtf.file import FileField
from wtforms.fields.html5 import DateField


class ProfileRedactForm(FlaskForm):
    image = FileField('Фотография')
    hometown = StringField('Город')
    birthday = DateField('Дата рождения')
    about = TextAreaField('Немного о себе')
    submit = SubmitField('Принять')
