from flask import jsonify
from flask_restful import Resource, abort, reqparse
from .db_session import create_session
from .users import Users
import datetime

parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)
parser.add_argument('about')
parser.add_argument('hometown', required=True)
parser.add_argument('birthday', required=True, type=datetime.date)


def abort_if_not_found(id):
    session = create_session()
    items = session.query(Users).get(id)
    if not items:
        abort(404, message=f"user {id} not found")


class UsersResource(Resource):
    def get(self, id):
        abort_if_not_found(id)
        session = create_session()
        user = session.query(Users).get(id)
        return jsonify({'user': user.to_dict(only=(
            'id', 'name', 'surname', 'email', 'hometown', 'birthday', 'about'))})

    def put(self, id):
        abort_if_not_found(id)
        args = parser.parse_args()
        session = create_session()
        user = session.query(Users).get(id)
        user.surname = args['surname']
        user.name = args['name']
        user.email = args['email']
        user.about = args['about']
        user.hometown = args['hometown']
        user.birthday = args['birthday']
        session.merge(user)
        session.commit()


class UsersListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(Users).all()
        return jsonify({'users': [user.to_dict(
            only=('id', 'name', 'surname', 'email',
                  'hometown', 'birthday', 'about')) for user in users]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        user = Users(surname=args['surname'],
                     name=args['name'],
                     email=args['email'],
                     about=args['about'],
                     hometown=args['hometown'],
                     birthday=args['birthday'])
        user.set_password(args['password'])
        session.add(user)
        session.commit()
