from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Post, session
from datetime import datetime
import json

posts_bp = Blueprint('posts_bp', __name__)

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = session.query(Post).all()
    return jsonify([post.to_dict() for post in posts])

@posts_bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = session.query(Post).get(id)
    if post is None:
        abort(404, description="Post not found")
    return jsonify(post.to_dict())

@posts_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    current_user = json.loads(get_jwt_identity())
    new_post = Post(
        title=data['title'],
        content=data['content'],
        user_id=current_user['id'],
        category_id=data['category_id'],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(new_post)
    session.commit()
    return jsonify(new_post.to_dict()), 201

@posts_bp.route('/posts/<int:id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    post = session.query(Post).get(id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    data = request.get_json()
    current_user = json.loads(get_jwt_identity()) 
    if post.user_id != current_user['id']:
        return jsonify({"message": "You can't update this posts."}), 403

    post.title = data['title']
    post.content = data['content']
    post.category_id = data['category_id']
    post.updated_at = datetime.utcnow()
    session.commit()
    return jsonify(post.to_dict()), 200
@posts_bp.route('/posts/<int:id>', methods=['DELETE'])
@jwt_required()
@jwt_required()
def delete_post(id):
    try:
        post = session.query(Post).get(id)
        if not post:
            return jsonify({"message": "Post not found"}), 404

        current_user = json.loads(get_jwt_identity())
        if post.user_id != current_user['id']:
            return jsonify({"message": "You can't  delete this post."}), 403

        session.delete(post)
        session.commit()
        return jsonify({"message": "Post deleted successfully."}), 200
    except Exception as e:
        session.rollback()  
        return jsonify({"message": "An error occurred while deleting the post.", "error": str(e)}), 500