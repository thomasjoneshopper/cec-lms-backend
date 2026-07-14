from flask import Blueprint, abort, jsonify, g, request
from pydantic import BaseModel

from cec_lms_backend import db
from cec_lms_backend.auth import verify_user, verify_json, verify_empty

paragraph = Blueprint("paragraph", __name__, url_prefix="/paragraph/<int:paragraph_id>")

@paragraph.url_value_preprocessor
def verify_course_id(endpoint, values: dict):
    g.paragraph_id = values.pop("paragraph_id", None)

@paragraph.post("/completion")
@verify_empty
def post_completion():
    if db.content.save_progress(g.user_id, g.paragraph_id):
        return jsonify(success=True)
    else:
        return abort(404)