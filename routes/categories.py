from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from routes.auth import role_required
from models import Category, session
import json

categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = session.query(Category).all()
    return jsonify([category.to_dict() for category in categories])

@categories_bp.route('/categories', methods=['POST'])
@jwt_required()
@role_required("admin")
def create_category():
    data = request.get_json()
    new_category = Category(name=data['name'])
    session.add(new_category)
    session.commit()
    return jsonify(new_category.to_dict()), 201
