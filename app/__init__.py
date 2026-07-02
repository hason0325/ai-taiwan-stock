from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 確保 instance 目錄存在
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    db.init_app(app)

    from app.routes import web, api
    app.register_blueprint(web.bp)
    app.register_blueprint(api.bp)

    return app