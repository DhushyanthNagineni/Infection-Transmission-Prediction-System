from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import DATABASE_URL

db = SQLAlchemy()

def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
