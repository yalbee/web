from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class NewForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    category = RadioField('Категория', choices=[('Спорт', 'Спорт'), ('Музыка', 'Музыка'),
                                                ('Политика', 'Политика'), ('IT', 'IT'),
                                                ('Искусство', 'Искусство'), ('Наука', 'Наука'),
                                                ('Юмор', 'Юмор'), ('Другое', 'Другое')],
                          validators=[DataRequired()])
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Создать')
