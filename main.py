from flask import Flask, render_template, redirect, jsonify, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_restful import Api
from flask_jwt_simple import JWTManager
from data.models.db_session import create_session, global_init
from data.models.users import Users
from data.models.news import News
from data.models.subscriptions import Subscriptions
from data.forms.register import RegisterForm
from data.forms.login import LoginForm
from data.forms.create_new import NewForm
from data.forms.redact_profile import ProfileRedactForm
from data.forms.change_password import ChangePasswordForm
from data.users_resource import RegisterResource, LoginResource, UsersResource, UsersListResource
from data.news_resource import NewsResource, NewsListResource
from PIL import Image, UnidentifiedImageError
import random
import datetime

app = Flask(__name__)
api = Api(app)
api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginResource, '/api/login')
api.add_resource(UsersResource, '/api/users/<int:id>')
api.add_resource(UsersListResource, '/api/users')
api.add_resource(NewsResource, '/api/news/<int:id>')
api.add_resource(NewsListResource, '/api/news')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['JWT_SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['JWT_EXPIRES'] = datetime.timedelta(hours=24)
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_IDENTITY_CLAIM'] = 'user'
app.jwt = JWTManager()
app.jwt.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/data.db')


@app.jwt.expired_token_loader
def expired_token_callback():
    return jsonify({'error': 'expired token'}, 401)


@app.jwt.unauthorized_loader
@app.jwt.invalid_token_loader
def unauth_inv_token_callback(why):
    return jsonify({'error': why}, 401)


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
        return redirect(f'/users/{current_user.id}')
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


@app.route('/users/<id>')
@login_required
def profile(id):
    session = create_session()
    user = session.query(Users).get(id)
    news = session.query(News).filter(News.creator == id).order_by(News.datetime.desc())
    title = f'{user.name} {user.surname}'
    subscribed = session.query(Subscriptions).filter(Subscriptions.user_id == current_user.id,
                                                     Subscriptions.sub == id).first()
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('profile.html', title=title, user=user, news=news, subscribed=subscribed, liked=liked)


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
        user.hometown = form.hometown.data
        user.birthday = form.birthday.data
        user.about = form.about.data
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('redact_profile.html', title='Редактировать профиль', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('change_password.html', title='Смена пароля',
                                   form=form,
                                   message="Пароли не совпадают")
        session = create_session()
        current_user.set_password(form.password.data)
        session.merge(current_user)
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('change_password.html', title='Смена пароля', form=form)


@app.route('/news')
@login_required
def show_news():
    session = create_session()
    news = session.query(News).filter(News.creator != current_user.id).order_by(News.datetime.desc()).all()
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('news.html', title='Новости', news=news, liked=liked)


@app.route('/categories')
@login_required
def categories():
    return render_template('categories.html', title='Категории')


@app.route('/news/<category>')
@login_required
def news_by_category(category):
    session = create_session()
    news = session.query(News).filter(News.creator != current_user.id,
                                      News.category == category).order_by(News.datetime.desc()).all()
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('news.html', title=category, news=news, liked=liked)


@app.route('/create_news', methods=['GET', 'POST'])
@login_required
def create_new():
    form = NewForm()
    if form.validate_on_submit():
        session = create_session()
        new = News(creator=current_user.id, title=form.title.data,
                   category=form.category.data, content=form.content.data,
                   datetime=datetime.datetime.now())
        new.string_dt = new.datetime.strftime('%m/%d %H:%M')
        session.add(new)
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('create_new.html', title='Создать запись', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def redact_new(id):
    form = NewForm()
    if form.validate_on_submit():
        session = create_session()
        new = session.query(News).get(id)
        new.title = form.title.data
        new.category = form.category.data
        new.content = form.content.data
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('create_new.html', title='Редактировать запись', form=form, id=id)


@app.route('/delete_new/<int:id>')
@login_required
def delete_new(id):
    session = create_session()
    new = session.query(News).get(id)
    session.delete(new)
    session.commit()
    return redirect(f'/users/{current_user.id}')


@app.route('/like/<int:id>')
@login_required
def like(id):
    session = create_session()
    new = session.query(News).get(id)
    new.likes += 1
    liked = current_user.liked_news.split()
    liked.append(str(id))
    current_user.liked_news = ' '.join(liked)
    session.merge(current_user)
    session.merge(new)
    session.commit()
    return redirect('/liked_news')


@app.route('/unlike/<int:id>')
@login_required
def unlike(id):
    session = create_session()
    new = session.query(News).get(id)
    new.likes -= 1
    liked = current_user.liked_news.split()
    liked.remove(str(id))
    current_user.liked_news = ' '.join(liked)
    session.merge(current_user)
    session.merge(new)
    session.commit()
    return redirect('/liked_news')


@app.route('/liked_news')
@login_required
def liked_news():
    session, news = create_session(), []
    for id in current_user.liked_news.split():
        news.append(session.query(News).get(id))
    news = sorted(news, key=lambda x: x.datetime)
    news.reverse()
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('news.html', title='Понравившееся', news=news, liked=liked)


@app.route('/my_subscriptions')
@login_required
def my_subscriptions():
    session, users = create_session(), []
    for subscription in current_user.subscriptions:
        users.append(session.query(Users).get(subscription.sub))
    return render_template('subscriptions.html', users=users, title='Мои подписки')


@app.route('/subscribers/<int:id>')
@login_required
def subscribers(id):
    session, users = create_session(), []
    user = session.query(Users).get(id)
    for subscriber in user.subscribers.split():
        users.append(session.query(Users).get(int(subscriber)))
    return render_template('subscriptions.html', users=users,
                           subs_count=user.subs_count, title='Подписчики')


@app.route('/subscribe/<int:id>')
@login_required
def subscribe(id):
    session = create_session()
    user = session.query(Users).get(id)
    subscription = Subscriptions(sub=id)
    current_user.subscriptions.append(subscription)
    subscribers = user.subscribers.split()
    subscribers.append(str(current_user.id))
    user.subscribers = ' '.join(subscribers)
    user.subs_count += 1
    session.merge(current_user)
    session.merge(user)
    session.commit()
    return redirect(f'/users/{id}')


@app.route('/unsubscribe/<int:id>')
@login_required
def unsubscribe(id):
    session = create_session()
    user = session.query(Users).get(id)
    subscription = session.query(Subscriptions).filter(Subscriptions.user_id == current_user.id,
                                                       Subscriptions.sub == id).first()
    session.delete(subscription)
    subscribers = user.subscribers.split()
    subscribers.remove(str(current_user.id))
    user.subscribers = ' '.join(subscribers)
    user.subs_count -= 1
    session.merge(current_user)
    session.merge(user)
    session.commit()
    return redirect(f'/users/{id}')


@app.errorhandler(401)
def unauthorized(error):
    return redirect('/login')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
