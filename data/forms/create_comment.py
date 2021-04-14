from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    comment = StringField(validators=[DataRequired()])
    submit = SubmitField('Оставить комментарий')
