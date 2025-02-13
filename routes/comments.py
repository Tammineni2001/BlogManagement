from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Comment, Post, session
from datetime import datetime
import json

comments_bp = Blueprint('comments_bp', __name__)

@comments_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = session.query(Comment).filter_by(post_id=post_id).all()
    return jsonify([comment.to_dict() for comment in comments])

@comments_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    
    post = session.query(Post).get(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    current_user = json.loads(get_jwt_identity())

    if post.user_id != current_user['id']:
        return jsonify({"message": "You are not allowed to comment on this post."}), 403

    data = request.get_json()
    new_comment = Comment(
        content=data['content'],
        post_id=post_id,
        user_id=current_user['id'],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(new_comment)
    session.commit()
    return jsonify(new_comment.to_dict()), 201