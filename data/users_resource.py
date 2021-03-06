from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from .models.db_session import create_session
from .models.users import Users
from flask_jwt_simple import jwt_required, create_jwt
import datetime

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


def create_jwt_for_user(user):
    return make_response(jsonify({'token': 'Bearer ' + create_jwt(identity=user)}), 200)


class RegisterResource(Resource):
    def post(self):
        args = register_parser.parse_args()
        session = create_session()
        if session.query(Users).filter(Users.email == args['email']).first():
            return make_response(jsonify({'error': 'user already exists'}), 400)
        user = Users(surname=args['surname'],
                     name=args['name'],
                     email=args['email'],
                     about=args['about'],
                     hometown=args['hometown'])
        try:
            date = datetime.datetime.strptime(args['birthday'], '%d/%m/%Y')
            user.birthday = date.date()
        except ValueError:
            return make_response(jsonify({'error': 'wrong date'}), 400)
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
            return make_response(jsonify({'error': 'wrong email or password'}), 400)


class UsersResource(Resource):
    @jwt_required
    def get(self, id):
        session = create_session()
        user = session.query(Users).get(id)
        if not user:
            return make_response(jsonify({'error': f'user {id} not found'}), 404)
        return jsonify({'user': user.to_dict(only=[
            'id', 'surname', 'name', 'hometown', 'birthday', 'about'])})


class UsersListResource(Resource):
    @jwt_required
    def get(self):
        session = create_session()
        users = session.query(Users).all()
        return jsonify({'users': [user.to_dict(only=[
            'id', 'surname', 'name', 'hometown', 'birthday', 'about']) for user in users]})
