import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Chats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String)
    chat = sqlalchemy.Column(sqlalchemy.Integer)
    last_message = sqlalchemy.Column(sqlalchemy.String)
    last_message_dt = sqlalchemy.Column(sqlalchemy.DateTime)
    user = orm.relation('Users')
    messages = orm.relation("Messages", back_populates='chat')
