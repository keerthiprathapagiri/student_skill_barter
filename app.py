# app.py – Entry point for Student Skill Barter

from flask import Flask
from flask_socketio import SocketIO
from config import ActiveConfig
from database.db import db
import os


def create_app():
    """Create and configure Flask app."""

    # Get the absolute path to the static folder
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    app.config.from_object(ActiveConfig)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)

    # Import models BEFORE create_all()
    # Add all your models here
    try:
        from models.user import User

        # If you have message model:
        # from models.message import Message

    except Exception as e:
        print(f"Model import warning: {e}")

    # Create tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database error: {e}")

    return app


# Create Flask app
app = create_app()

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

# Register socket events
try:
    from routes.chat import init_socketio
    init_socketio(socketio)
    print("✅ SocketIO initialized")
except Exception as e:
    print(f"❌ SocketIO error: {e}")


if __name__ == "__main__":
    print("\n⚡ Student Skill Barter → http://localhost:5000\n")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=ActiveConfig.DEBUG
    )
