import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Messages(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('chats.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer)  # id отправителя
    message = sqlalchemy.Column(sqlalchemy.String)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime)
    string_dt = sqlalchemy.Column(sqlalchemy.String)
    chat = orm.relation('Chats')
