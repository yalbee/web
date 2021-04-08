import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
import datetime


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String)
    category = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    user = orm.relation('Users')
