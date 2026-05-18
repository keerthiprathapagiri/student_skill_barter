# app.py – Entry point for Student Skill Barter

from flask import Flask
from flask_socketio import SocketIO
from config import ActiveConfig
from database.db import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(ActiveConfig)

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


app = create_app()

socketio = SocketIO(
    app,
    cors_allowed_origins='*',
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

from routes.chat import init_socketio
init_socketio(socketio)


if __name__ == '__main__':
    print('\n  ⚡ Student Skill Barter → http://localhost:5000\n')

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=ActiveConfig.DEBUG
    )