from flask import Blueprint, request, jsonify
from models import User, session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from db import initialize_connection
from functools import wraps
import json



auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
bcrypt = Bcrypt()

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = json.loads(get_jwt_identity())
            print(f"Identity: {identity}")  
            if not identity or identity.get("role") != required_role:
                return jsonify({"success": False, "message": "Access forbidden"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@auth_bp.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = request.json.get("email")
        confirm_password = request.json.get("confirm_password")
        role = request.json.get("role")

        if password != confirm_password:
            return jsonify({"success": False, "message": "Passwords do not match"}), 400

        if not role or role not in ["user", "admin"]:
            return jsonify({"success": False, "message": "Invalid role. Role must be 'user' or 'admin'."}), 400

        engine, session, Base = initialize_connection("JR_TRAINING_DB")

        try:
            query = text("SELECT * FROM public.users WHERE name = :username OR mail = :email")
            result = session.execute(query, {"username": username, "email": email})
            res = result.fetchall()

            for user_data in res:
                if user_data[1] == username or user_data[2] == email: 
                    return jsonify({"success": False, "message": "User already exists"}), 400

            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

            insert_query = text("""
                INSERT INTO public.users (name, mail, password, role)
                VALUES (:username, :email, :password_hash, :role)
            """)
            session.execute(insert_query, {"username": username, "email": email, "password_hash": password_hash, "role": role})
            session.commit()

            return jsonify({"success": True, "message": "User registered successfully"}), 201

        except Exception as e:
            session.rollback()
            return jsonify({"success": False, "message": "An error occurred during registration", "error": str(e)}), 500

        finally:
            session.close()

    else:
        errors = form.errors
        return jsonify({"success": False, "message": "Validation failed", "errors": errors}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = request.json.get("email")

        engine, session, Base = initialize_connection("JR_TRAINING_DB")

        try:
            query = text("SELECT * FROM public.users WHERE name = :username AND mail = :email")
            result = session.execute(query, {"username": username, "email": email}).mappings()
            res = result.fetchall()

            if not res:
                return jsonify({"success": False, "message": "Invalid Username or Email"}), 400

            for user_data in res:
                if bcrypt.check_password_hash(user_data["password"], password):
                    identity = json.dumps({"id": user_data["id"], "username": username, "role": user_data["role"]})
                    access_token = create_access_token(identity=identity)
                    return jsonify({"success": True, "message": "Login successful", "access_token": access_token}), 200
                else:
                    return jsonify({"success": False, "message": "Invalid Password"}), 400

        except Exception as e:
            return jsonify({"success": False, "message": "An error occurred during login", "error": str(e)}), 500

        finally:
            session.close()

    else:
        errors = form.errors
        return jsonify({"success": False, "message": "Validation failed", "errors": errors}), 400
