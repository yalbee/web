import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm

association_table = sqlalchemy.Table(
    'users_to_chats',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('user', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('chat', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('chats.id')))


class Chats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    last_message = sqlalchemy.Column(sqlalchemy.String)
    last_message_dt = sqlalchemy.Column(sqlalchemy.DateTime)
    private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    users = orm.relation('Users', secondary="users_to_chats", backref="chat")
    messages = orm.relation("Messages", back_populates='chat')
