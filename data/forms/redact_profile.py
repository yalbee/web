from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField


class ProfileRedactForm(FlaskForm):
    image = FileField('Фотография')
    about = TextAreaField('Немного о себе')
    submit = SubmitField('Принять')
