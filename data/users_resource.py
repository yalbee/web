from flask import jsonify
from flask_restful import Resource, abort, reqparse
from .db_session import create_session
from .users import Users
import datetime

put_parser = reqparse.RequestParser()
put_parser.add_argument('password', required=True)
put_parser.add_argument('about')
put_parser.add_argument('hometown', required=True)
put_parser.add_argument('birthday', required=True, type=datetime.date)

post_parser = reqparse.RequestParser()
post_parser.add_argument('surname', required=True)
post_parser.add_argument('name', required=True)
post_parser.add_argument('email', required=True)
post_parser.add_argument('password', required=True)
post_parser.add_argument('about')
post_parser.add_argument('hometown', required=True)
post_parser.add_argument('birthday', required=True, type=datetime.date)


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
        args = put_parser.parse_args()
        session = create_session()
        user = session.query(Users).get(id)
        user.about = args['about']
        user.hometown = args['hometown']
        user.birthday = args['birthday']
        user.set_password(args['password'])
        session.merge(user)
        session.commit()
        return jsonify({'success': 'ok'})


class UsersListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(Users).all()
        return jsonify({'users': [user.to_dict(
            only=('id', 'name', 'surname', 'email',
                  'hometown', 'birthday', 'about')) for user in users]})

    def post(self):
        args = post_parser.parse_args()
        session = create_session()
        if session.query(Users).filter(Users.email == args['email']).first():
            return jsonify({'error': 'user already exists'})
        user = Users(surname=args['surname'],
                     name=args['name'],
                     email=args['email'],
                     about=args['about'],
                     hometown=args['hometown'],
                     birthday=args['birthday'])
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'ok'})
