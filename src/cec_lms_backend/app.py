from flask import Flask, jsonify, current_app, request
from pyodbc import Error as DBError
from werkzeug.exceptions import NotFound, MethodNotAllowed

from cec_lms_backend.endpoints import auth, course, paragraph, quiz


def not_found(error: NotFound):
    return jsonify(
        error=f"{error.code} {error.name}",
        message=f"URL '{request.base_url}' does not exist"
    ), 404

def method_not_allowed(error: MethodNotAllowed):
    return jsonify(
        error=f"{error.code} {error.name}",
        message=f"Method '{request.method}' not allowed for URL '{request.base_url}'"
    ), 405

def db_error(error: DBError):
    current_app.logger.exception(error)
    return jsonify(
        error="500 Internal Server Error",
        message="An unexpected error occured"
    ), 500


def create_app() -> Flask:

    app = Flask(__name__)

    app.json.sort_keys = False

    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(DBError, db_error)

    app.register_blueprint(auth)
    app.register_blueprint(course)
    app.register_blueprint(paragraph)
    app.register_blueprint(quiz)
    
    return app

