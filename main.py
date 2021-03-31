from flask import Flask, render_template, redirect, jsonify, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from data.db_session import create_session, global_init
from data.users import Users
from data.news import News
from data.forms.register import RegisterForm
from data.forms.login import LoginForm
from data.forms.create_new import NewForm
from data.forms.redact_profile import ProfileRedactForm
from PIL import Image, UnidentifiedImageError
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/data.db')


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(Users).get(user_id)


@app.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect('/news')
    session = create_session()
    news = session.query(News).all()
    if news:
        return render_template('welcome.html', title='НЕ ВК.com', new=random.choice(news))
    return render_template('base.html', title='НЕ ВК.com')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = Users(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            hometown=form.hometown.data,
            birthday=form.birthday.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news')
@login_required
def show_news():
    session = create_session()
    news = session.query(News).filter(News.creator != current_user.id)
    return render_template('news.html', title='Новости', news=news)


@app.route('/users/<id>')
@login_required
def profile(id):
    session = create_session()
    user = session.query(Users).get(id)
    title = f'{user.name} {user.surname}'
    session = create_session()
    return render_template('profile.html', title=title, user=user)


@app.route('/redact_profile', methods=['GET', 'POST'])
@login_required
def redact_profile():
    form = ProfileRedactForm()
    if form.validate_on_submit():
        session = create_session()
        user = session.query(Users).get(current_user.id)
        if form.image.data:
            try:
                image = Image.open(form.image.data)
                path = f'static/img/{current_user.id}.' + str(image.format).lower()
                image.save(path, format=image.format)
                user.image = '/' + path
            except UnidentifiedImageError:
                return render_template('redact_profile.html', title='Редактировать профиль',
                                       form=form, message='Это не фотография...')
        user.about = form.about.data
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('redact_profile.html', title='Редактировать профиль', form=form)


@app.route('/delete_profile')
@login_required
def delete_profile():
    session = create_session()
    user = session.query(Users).get(current_user.id)
    logout_user()
    session.delete(user)
    session.commit()
    return redirect('/')


@app.route('/create_news', methods=['GET', 'POST'])
@login_required
def create_new():
    form = NewForm()
    if form.validate_on_submit():
        session = create_session()
        new = News()
        new.creator = current_user.id
        new.content = form.content.data
        session.add(new)
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('create_new.html', title='Создать новость', form=form)


@app.errorhandler(401)
def not_found(error):
    return redirect('/login')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
