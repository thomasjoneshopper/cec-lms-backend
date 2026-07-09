from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from cec_lms_backend.auth import auth
from cec_lms_backend.course import course
from cec_lms_backend.quiz import quiz

def not_found(error: HTTPException):
    return jsonify(
        error=f"{error.code} {error.name}",
        message=f"URL '{request.base_url}' does not exist"
    ), 404

def method_not_allowed(error: HTTPException):
    return jsonify(
        error=f"{error.code} {error.name}",
        message=f"Method '{request.method}' not allowed for URL '{request.base_url}'"
    ), 405

def http_exception(error: HTTPException):
    return jsonify(
        error=f"{error.code} {error.name}",
        message=error.description
    )

def create_app() -> Flask:

    app = Flask(__name__)

    app.json.sort_keys = False

    app.register_blueprint(auth)
    app.register_blueprint(course)
    app.register_blueprint(quiz)

    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(HTTPException, http_exception)
    
    return app

