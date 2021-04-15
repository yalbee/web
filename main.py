from flask import Flask, render_template, redirect, jsonify, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_restful import Api
from flask_jwt_simple import JWTManager
from data.models.db_session import create_session, global_init
from data.models.users import Users
from data.models.news import News
from data.models.comments import Comments
from data.forms.register import RegisterForm
from data.forms.login import LoginForm
from data.forms.create_new import NewForm
from data.forms.create_comment import CommentForm
from data.forms.redact_profile import ProfileRedactForm
from data.forms.change_password import ChangePasswordForm
from data.users_resource import RegisterResource, LoginResource, UsersResource, UsersListResource
from data.news_resource import NewsResource, NewsListResource
from data.comments_resource import CommentsResource, CommentsListResource
from PIL import Image, UnidentifiedImageError
import random
import datetime
import os

app = Flask(__name__)
api = Api(app)
api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginResource, '/api/login')
api.add_resource(UsersResource, '/api/users/<int:id>')
api.add_resource(UsersListResource, '/api/users')
api.add_resource(NewsResource, '/api/news/<int:id>')
api.add_resource(NewsListResource, '/api/news')
api.add_resource(CommentsResource, '/api/comments/<int:id>')
api.add_resource(CommentsListResource, '/api/comments')
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
        return render_template('welcome.html', title='shitter.com', new=random.choice(news))
    return render_template('base.html', title='shitter.com')


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


@app.route('/users/<int:id>')
@login_required
def profile(id):
    session = create_session()
    user = session.query(Users).get(id)
    if not user:
        return not_found(404)
    news = session.query(News).filter(News.creator == id).order_by(News.datetime.desc())
    title = f'{user.name} {user.surname}'
    subscribed = bool(str(id) in current_user.subscriptions.split())
    return render_template('profile.html', title=title, user=user, news=news, subscribed=subscribed)


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
        if form.hometown.data != '':
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
    return render_template('news.html', title='Новости', news=news)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def new(id):
    session = create_session()
    new = session.query(News).get(id)
    if not new:
        return not_found(404)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comments(content=form.comment.data, creator=current_user.id)
        comment.datetime = datetime.datetime.now()
        comment.string_dt = comment.datetime.strftime('%m/%d %H:%M')
        new.comments.append(comment)
        session.commit()
        return redirect(f'/news/{id}')
    liked = bool(str(id) in current_user.liked_news.split())
    return render_template('new.html', new=new, liked=liked, title=new.title, form=form)


@app.route('/categories')
@login_required
def categories():
    return render_template('categories.html', title='Категории')


@app.route('/news/<category>')
@login_required
def news_by_category(category):
    if category not in ['Спорт', 'Музыка', 'Политика', 'IT',
                        'Искусство', 'Наука', 'Юмор', 'Другое']:
        return not_found(404)
    session = create_session()
    news = session.query(News).filter(News.creator != current_user.id,
                                      News.category == category).order_by(News.datetime.desc()).all()
    return render_template('news.html', title=category, news=news)


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


@app.route('/redact_new/<int:id>', methods=['GET', 'POST'])
@login_required
def redact_new(id):
    session = create_session()
    new = session.query(News).get(id)
    if not new:
        return not_found(404)
    if current_user.id != new.creator:
        return make_response(jsonify({'error': 'you are not creator of this new'}), 403)
    form = NewForm()
    if form.validate_on_submit():
        new.title = form.title.data
        new.category = form.category.data
        new.content = form.content.data
        session.commit()
        return redirect(f'/news/{id}')
    return render_template('create_new.html', title='Редактировать запись', form=form, id=id)


@app.route('/delete_new/<int:id>')
@login_required
def delete_new(id):
    session = create_session()
    new = session.query(News).get(id)
    if not new:
        return not_found(404)
    if current_user.id != new.creator:
        return make_response(jsonify({'error': 'you are not creator of this new'}), 403)
    session.delete(new)
    session.commit()
    return redirect(f'/users/{current_user.id}')


@app.route('/delete_comment/<int:id>')
@login_required
def delete_comment(id):
    session = create_session()
    comment = session.query(Comments).get(id)
    if not comment:
        return not_found(404)
    if current_user.id != comment.creator:
        return make_response(jsonify({'error': 'you are not creator of this comment'}), 403)
    new_id = comment.new.id
    session.delete(comment)
    session.commit()
    return redirect(f'/news/{new_id}')


@app.route('/like/<int:id>')
@login_required
def like(id):
    session = create_session()
    new = session.query(News).get(id)
    if not new:
        return not_found(404)
    if str(id) in current_user.liked_news.split() or new.creator == current_user.id:
        return make_response(jsonify({'error': 'bad request'}), 400)
    new.likes += 1
    liked = current_user.liked_news.split()
    liked.append(str(id))
    current_user.liked_news = ' '.join(liked)
    session.merge(current_user)
    session.merge(new)
    session.commit()
    return redirect(f'/news/{id}')


@app.route('/unlike/<int:id>')
@login_required
def unlike(id):
    session = create_session()
    new = session.query(News).get(id)
    if not new:
        return not_found(404)
    if str(id) not in current_user.liked_news.split() or new.creator == current_user.id:
        return make_response(jsonify({'error': 'bad request'}), 400)
    new.likes -= 1
    liked = current_user.liked_news.split()
    liked.remove(str(id))
    current_user.liked_news = ' '.join(liked)
    session.merge(current_user)
    session.merge(new)
    session.commit()
    return redirect(f'/news/{id}')


@app.route('/liked_news')
@login_required
def liked_news():
    session, news = create_session(), []
    news = [session.query(News).get(int(id)) for id in current_user.liked_news.split()]
    return render_template('news.html', title='Понравившееся', news=news)


@app.route('/my_subscriptions')
@login_required
def my_subscriptions():
    session = create_session()
    users = [session.query(Users).get(int(id)) for id in current_user.subscriptions.split()]
    return render_template('subscriptions.html', users=users, title='Мои подписки')


@app.route('/subscribers/<int:id>')
@login_required
def subscribers(id):
    session = create_session()
    user = session.query(Users).get(id)
    users = [session.query(Users).get(int(id)) for id in user.subscribers.split()]
    return render_template('subscriptions.html', users=users,
                           subs_count=user.subs_count, title='Подписчики')


@app.route('/subscribe/<int:id>')
@login_required
def subscribe(id):
    session = create_session()
    user = session.query(Users).get(id)
    if not user:
        return not_found(404)
    subscriptions = current_user.subscriptions.split()
    if str(id) in subscriptions or id == current_user.id:
        return make_response(jsonify({'error': 'bad request'}), 400)
    subscriptions.append(str(id))
    current_user.subscriptions = ' '.join(subscriptions)
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
    if not user:
        return not_found(404)
    subscriptions = current_user.subscriptions.split()
    if str(id) not in subscriptions or id == current_user.id:
        return make_response(jsonify({'error': 'bad request'}), 400)
    subscriptions.remove(str(id))
    current_user.subscriptions = ' '.join(subscriptions)
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
