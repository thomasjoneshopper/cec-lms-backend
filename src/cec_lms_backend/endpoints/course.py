from flask import Blueprint, abort, jsonify, g, request
from pydantic import BaseModel

from cec_lms_backend import db
from cec_lms_backend.endpoints.auth import verify_user, verify_json, verify_empty

course = Blueprint("course", __name__, url_prefix="/course/<int:course_id>")

@course.url_value_preprocessor
def verify_course_id(endpoint, values: dict):
    course_id = values.pop("course_id", None)
    if not db.content.course_exists(course_id):
        abort(404)
    g.course_id = course_id

@course.get("/progress")
@verify_user()
@verify_empty
def get_progress():
    progress = db.content.get_progress(g.user_id, g.course_id)
    return jsonify(progress)

@course.delete("/progress")
@verify_user(roles=["admin"]) # should require admin
def delete_progress():
    return f"deleting progress for user {g.user_id} in course {g.course_id}\n", 200
