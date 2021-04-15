from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from .models.db_session import create_session
from .models.news import News
from .models.comments import Comments
from flask_jwt_simple import jwt_required, get_jwt_identity
import datetime

parser = reqparse.RequestParser()
parser.add_argument('content', required=True)
parser.add_argument('new_id', required=True, type=int)


class CommentsResource(Resource):
    @jwt_required
    def get(self, id):
        session = create_session()
        comment = session.query(Comments).get(id)
        if not comment:
            return make_response(jsonify({'error': f'new {id} not found'}), 404)
        return jsonify({'comment': comment.to_dict(only=[
            'id', 'creator', 'new_id', 'content', 'datetime'])})

    @jwt_required
    def delete(self, id):
        session = create_session()
        comment = session.query(Comments).get(id)
        if not comment:
            return make_response(jsonify({'error': f'new {id} not found'}), 404)
        if comment.creator != get_jwt_identity()['id']:
            return make_response(jsonify({'error': 'you are not creator of this comment'}), 403)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'ok'})


class CommentsListResource(Resource):
    @jwt_required
    def get(self):
        session = create_session()
        comments = session.query(Comments).all()
        return jsonify({'comments': [comment.to_dict(only=[
            'id', 'creator', 'new_id', 'content', 'datetime']) for comment in comments]})

    @jwt_required
    def post(self):
        args = parser.parse_args()
        session = create_session()
        id = args['new_id']
        new = session.query(News).get(id)
        if not new:
            return make_response(jsonify({'error': f'new {id} not found'}), 404)
        comment = Comments(content=args['content'])
        comment.datetime = datetime.datetime.now()
        comment.string_dt = comment.datetime.strftime('%m/%d %H:%M')
        comment.creator = get_jwt_identity()['id']
        new.comments.append(comment)
        session.commit()
        return jsonify({'success': 'ok'})
