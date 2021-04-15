from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from .models.db_session import create_session
from .models.news import News
from flask_jwt_simple import jwt_required, get_jwt_identity
import datetime

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('category', required=True, help='Спорт/Музыка/Политика/IT/Искусство/Наука/Юмор/Другое')
parser.add_argument('content', required=True)


class NewsResource(Resource):
    @jwt_required
    def get(self, id):
        session = create_session()
        new = session.query(News).get(id)
        if not new:
            return make_response(jsonify({'error': f'new {id} not found'}), 404)
        return jsonify({'new': new.to_dict(only=[
            'id', 'creator', 'title', 'category', 'content', 'likes', 'datetime'])})

    @jwt_required
    def delete(self, id):
        session = create_session()
        new = session.query(News).get(id)
        if not new:
            return make_response(jsonify({'error': f'new {id} not found'}), 404)
        if new.creator != get_jwt_identity()['id']:
            return make_response(jsonify({'error': 'you are not creator of this new'}), 403)
        session.delete(new)
        session.commit()
        return jsonify({'success': 'ok'})

    @jwt_required
    def put(self, id):
        args = parser.parse_args()
        session = create_session()
        new = session.query(News).get(id)
        if not new:
            return make_response(jsonify({'error': f'new {id} not found'}), 404)
        if new.creator != get_jwt_identity()['id']:
            return make_response(jsonify({'error': 'you are not creator of this new'}), 403)
        if args['category'] not in ['Спорт', 'Музыка', 'Политика', 'IT',
                                    'Искусство', 'Наука', 'Юмор', 'Другое']:
            return make_response(jsonify({'error': 'invalid category'}), 400)
        new.title = args['title']
        new.category = args['category']
        new.content = args['content']
        session.merge(new)
        session.commit()
        return jsonify({'success': 'ok'})


class NewsListResource(Resource):
    @jwt_required
    def get(self):
        session = create_session()
        news = session.query(News).all()
        return jsonify({'news': [new.to_dict(only=[
            'id', 'creator', 'title', 'category', 'content', 'likes', 'datetime']) for new in news]})

    @jwt_required
    def post(self):
        args = parser.parse_args()
        session = create_session()
        if args['category'] not in ['Спорт', 'Музыка', 'Политика', 'IT',
                                    'Искусство', 'Наука', 'Юмор', 'Другое']:
            return make_response(jsonify({'error': 'invalid category'}), 400)
        new = News(title=args['title'],
                   category=args['category'],
                   content=args['content'])
        new.datetime = datetime.datetime.now()
        new.string_dt = new.datetime.strftime('%m/%d %H:%M')
        new.creator = get_jwt_identity()['id']
        session.add(new)
        session.commit()
        return jsonify({'success': 'ok'})
