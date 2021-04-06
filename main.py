from flask import Flask, render_template, redirect, jsonify, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from data.db_session import create_session, global_init
from data.users import Users
from data.news import News
from data.friends import Friends
from data.chats import Chats
from data.messages import Messages
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
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('news.html', title='Новости', news=news, liked=liked)


@app.route('/users/<id>')
@login_required
def profile(id):
    session = create_session()
    user = session.query(Users).get(id)
    title = f'{user.name} {user.surname}'
    friend = session.query(Friends).filter(Friends.user_id == current_user.id, Friends.friend == id).first()
    request = bool(str(current_user.id) in user.friend_requests.split())
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('profile.html', title=title, user=user, friend=friend, request=request, liked=liked)


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


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def redact_new(id):
    form = NewForm()
    if form.validate_on_submit():
        session = create_session()
        new = session.query(News).get(id)
        new.content = form.content.data
        session.commit()
        return redirect(f'/users/{current_user.id}')
    return render_template('redact_new.html', title='Редактировать запись', form=form, id=id)


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
    liked = [int(id) for id in current_user.liked_news.split()]
    return render_template('news.html', title='Понравившееся', news=news, liked=liked)


@app.route('/friends/<int:id>')
@login_required
def friends(id):
    session, friends, requests = create_session(), [], []
    user = session.query(Users).get(id)
    for friend in user.friends:
        friends.append(session.query(Users).get(friend.friend))
    if user.id == current_user.id:
        for id in current_user.friend_requests.split():
            requests.append(session.query(Users).get(id))
    return render_template('friends.html', friends=friends, requests=requests,
                           friends_count=user.friends_count, title='Друзья')


@app.route('/add_friend/<int:id>')
@login_required
def add_friend(id):
    session = create_session()
    user = session.query(Users).get(id)
    my_requests, user_requests = current_user.friend_requests.split(), user.friend_requests.split()
    if str(id) in my_requests:  # если мы принимаем запрос в друзья
        friend = Friends(friend=id)
        current_user.friends.append(friend)
        current_user.friends_count += 1
        friend = Friends(friend=current_user.id)
        user.friends.append(friend)
        user.friends_count += 1
        my_requests.remove(str(id))
        current_user.requests_count -= 1
    else:  # если мы отправляем запрос в друзья
        user_requests.append(str(current_user.id))
        user.requests_count += 1
    current_user.friend_requests, user.friend_requests = ' '.join(my_requests), ' '.join(user_requests)
    session.merge(current_user)
    session.merge(user)
    session.commit()
    return redirect(f'/users/{id}')


@app.route('/cancel_request/<int:id>')
@login_required
def cancel_request(id):  # отмена запроса в друзья
    session = create_session()
    user = session.query(Users).get(id)
    requests = user.friend_requests.split()
    requests.remove(str(current_user.id))
    user.requests_count -= 1
    user.friend_requests = ' '.join(requests)
    session.merge(user)
    session.commit()
    return redirect(f'/users/{id}')


@app.route('/delete_friend/<int:id>')
@login_required
def delete_friend(id):
    session = create_session()
    user = session.query(Users).get(id)
    friend = session.query(Friends).filter(Friends.user_id == current_user.id, Friends.friend == id).first()
    session.delete(friend)
    current_user.friends_count -= 1
    friend = session.query(Friends).filter(Friends.user_id == id, Friends.friend == current_user.id).first()
    session.delete(friend)
    user.friends_count -= 1
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
