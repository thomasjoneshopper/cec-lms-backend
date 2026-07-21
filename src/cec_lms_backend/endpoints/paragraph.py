from flask import Blueprint, abort, jsonify, g

from cec_lms_backend import db
from cec_lms_backend.endpoints.auth import verify_user, verify_empty

paragraph = Blueprint("paragraph", __name__, url_prefix="/paragraph/<int:paragraph_id>")

@paragraph.url_value_preprocessor
def verify_paragraph_id(endpoint: str, values: dict):
    g.paragraph_id = values.pop("paragraph_id")
    if g.paragraph_id not in db.paragraphs.context_cache:
        abort(404)


@paragraph.post("/completion")
@verify_user()
@verify_empty
def post_completion():
    db.paragraphs.update_completion(g.user_id, g.paragraph_id)
    return jsonify(success=True), 200
