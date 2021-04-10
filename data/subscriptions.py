import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Subscriptions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    sub = sqlalchemy.Column(sqlalchemy.Integer)
    user = orm.relation('Users')
