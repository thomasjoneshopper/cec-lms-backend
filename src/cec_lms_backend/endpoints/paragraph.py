from flask import Blueprint, abort, jsonify, g, request
from pyodbc import Error as DB_Error

from cec_lms_backend import db
from cec_lms_backend.endpoints.auth import verify_user, verify_json, verify_empty

paragraph = Blueprint("paragraph", __name__, url_prefix="/paragraph/<int:paragraph_id>")

@paragraph.url_value_preprocessor()
def verify_paragraph_id(endpoint: str, values: dict):
    paragraph_id = values.pop("paragraph_id")
    g.context = db.content.get_paragraph_context(paragraph_id)
    if not g.context:
        abort(404)


@paragraph.post("/completion")
@verify_user()
@verify_empty
def post_completion():
    db.content.save_progress(g.user_id, **g.context)
    return jsonify(success=True), 200
