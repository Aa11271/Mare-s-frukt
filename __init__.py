# app/__init__.py
from flask import Flask
from .extensions import db, login_manager, bcrypt, cache
from .config import Config  # Make sure 'Config' is defined in 'config.py'
from .models import User  # This line ensures models are imported and recognized by SQLAlchemy
from .routes import configure_routes  # This function will set up your routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['CACHE_TYPE'] = 'simple'  # You can choose 'simple', 'memcached', 'redis', etc.


    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) 

    with app.app_context():
        db.create_all()

    configure_routes(app)

    return app
