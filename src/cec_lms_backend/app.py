"""Entry point for flask app. Defines app factory `create_app()` as well as error handling"""

from flask import Flask, jsonify, current_app, request
from pyodbc import Error as DBError
from werkzeug.exceptions import HTTPException, InternalServerError

from cec_lms_backend.endpoints import auth, course, paragraph, quiz, image
from cec_lms_backend.db import paragraphs, quizzes

def http_error(error: HTTPException):
    match error.code:
        case 404: msg = f"Endpoint '{request.path}' does not exist"
        case 405: msg = f"Method '{request.method}' not allowed for endpoint '{request.base_url}'"
        case _: msg = error.description

    return jsonify(
        error=f"{error.code} {error.name}",
        message = msg
    ), error.code

def db_error(error: DBError):
    current_app.logger.exception("Database Error")
    return http_error(InternalServerError())

def create_app() -> Flask:

    app = Flask(__name__)
    app.json.sort_keys = False

    print("loading paragraph cache ...", end="", flush=True)
    paragraphs.load_cache()
    print(" done")

    print("loading quiz cache ...", end="", flush=True)
    quizzes.load_cache()
    print(" done")

    app.register_error_handler(HTTPException, http_error)
    app.register_error_handler(DBError, db_error)

    app.register_blueprint(auth)
    app.register_blueprint(course)
    app.register_blueprint(paragraph)
    app.register_blueprint(quiz)
    app.register_blueprint(image)
    
    return app

