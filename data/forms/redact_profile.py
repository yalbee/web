from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from flask_wtf.file import FileField


class ProfileRedactForm(FlaskForm):
    image = FileField('Фотография')
    about = TextAreaField('Немного о себе')
    submit = SubmitField('Принять')
