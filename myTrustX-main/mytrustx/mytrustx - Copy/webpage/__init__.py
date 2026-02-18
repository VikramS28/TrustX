from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hahaj'  # Replace with os.urandom(24).hex() for security
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trustx.db'  # Use your database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warnings
    app.config['COINBASE_COMMERCE_API_KEY'] = '84b6c82c-da2a-444f-8426-d30cafd8030b'  # Replace with your API key

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Register blueprints
    from .view import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Create database tables (optional, for initial setup)
    with app.app_context():
        db.create_all()

    return app