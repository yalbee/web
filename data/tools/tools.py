from flask import make_response, jsonify
from flask_jwt_simple import create_jwt


def make_resp(message, status):
    response = make_response(message, status)
    response.headers['Content_type'] = 'application/json; charset=utf-8'
    return response


def create_jwt_for_user(user):
    return make_resp(jsonify({'token': 'Bearer ' + create_jwt(identity=user)}), 200)
