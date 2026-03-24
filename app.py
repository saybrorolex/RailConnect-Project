from flask import Flask
from config import Config
from extensions import db, login_manager
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.trains import trains_bp
from routes.bookings import bookings_bp
from routes.analytics import analytics_bp
from routes.search import search_bp
from routes.fare import fare_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(trains_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(fare_bp)

    return app

# Expose app at module level for Gunicorn: gunicorn "app:app"
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
