from flask import jsonify
from flask_restful import Resource, reqparse
from .db_session import create_session
from .users import Users
import datetime
from .tools.tools import make_resp, create_jwt_for_user

register_parser = reqparse.RequestParser()
register_parser.add_argument('surname', required=True)
register_parser.add_argument('name', required=True)
register_parser.add_argument('email', required=True)
register_parser.add_argument('password', required=True)
register_parser.add_argument('about', required=True)
register_parser.add_argument('hometown', required=True)
register_parser.add_argument('birthday', required=True, help='date format: d/m/Y  # 01/01/1999')

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', required=True)
login_parser.add_argument('password', required=True)


class RegisterResource(Resource):
    def post(self):
        args = register_parser.parse_args()
        session = create_session()
        if session.query(Users).filter(Users.email == args['email']).first():
            return make_resp(jsonify({'error': 'user already exists'}), 400)
        user = Users(surname=args['surname'],
                     name=args['name'],
                     email=args['email'],
                     about=args['about'],
                     hometown=args['hometown'])
        try:
            date = datetime.datetime.strptime(args['birthday'], '%d/%m/%Y')
            user.birthday = date.date()
        except ValueError:
            return make_resp(jsonify({'error': 'wrong date'}), 400)
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        id = session.query(Users).filter(Users.email == user.email).first().id
        return create_jwt_for_user({'id': id, 'email': user.email})


class LoginResource(Resource):
    def post(self):
        args = login_parser.parse_args()
        session = create_session()
        user = session.query(Users).filter(Users.email == args['email']).first()
        if user and user.check_password(args['password']):
            return create_jwt_for_user({'id': user.id, 'email': user.email})
        else:
            return make_resp(jsonify({'error': 'wrong email or password'}), 400)


class UsersResource(Resource):
    def get(self, id):
        session = create_session()
        user = session.query(Users).get(id)
        if not user:
            return make_resp(jsonify({'error': f'user {id} not found'}), 400)
        return jsonify({'user': user.to_dict(only=[
            'id', 'surname', 'name', 'hometown', 'birthday', 'about'])})


class UsersListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(Users).all()
        return jsonify({'users': [user.to_dict(only=[
            'id', 'surname', 'name', 'hometown', 'birthday', 'about']) for user in users]})
