import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Comments(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    new_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news.id'))
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    content = sqlalchemy.Column(sqlalchemy.String)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime)
    string_dt = sqlalchemy.Column(sqlalchemy.String)
    new = orm.relation('News')
    user = orm.relation('Users')
