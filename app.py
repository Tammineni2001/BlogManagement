from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flasgger import Swagger
from flask_swagger_ui import  get_swaggerui_blueprint
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.categories import categories_bp

app = Flask(__name__)
app.config.from_object('config.Config')

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

# Swagger configuration
SWAGGER_URL = '/api-docs'  # New URL
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Blog Management System API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

Swagger(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(posts_bp, url_prefix='/api')
app.register_blueprint(comments_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Blog Management System API!'})

if __name__ == '__main__':
    app.run(debug=True)