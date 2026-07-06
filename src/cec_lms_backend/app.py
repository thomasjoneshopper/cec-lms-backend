from flask import Flask

from .auth import auth
from .course import course
from .quiz import quiz

def create_app() -> Flask:

    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(course)
    app.register_blueprint(quiz)
    
    return app