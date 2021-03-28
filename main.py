from flask import Flask, render_template, redirect
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from data.db_session import create_session, global_init
from data.users import Users
from data.forms.register import RegisterForm
from data.forms.login import LoginForm

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
def start_page():
    return render_template('start_page.html', title='Добро пожаловать')


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


@app.route('/user/<id>')
@login_required
def profile(id):
    session = create_session()
    user = session.query(Users).get(id)
    title = f'{user.name} {user.surname}'
    return render_template('profile.html', title=title, user=user)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
