import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hometown = sqlalchemy.Column(sqlalchemy.String)
    birthday = sqlalchemy.Column(sqlalchemy.Date)
    image = sqlalchemy.Column(sqlalchemy.String, default='/static/img/0.jpeg')
    subscriptions = sqlalchemy.Column(sqlalchemy.String, default='')  # подписки пользователя
    subscribers = sqlalchemy.Column(sqlalchemy.String, default='')  # подписчики
    subs_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # количество подписчиков
    liked_news = sqlalchemy.Column(sqlalchemy.String, default='')  # понравившиеся записи
    news = orm.relation("News", back_populates='user')
    comments = orm.relation("Comments", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
