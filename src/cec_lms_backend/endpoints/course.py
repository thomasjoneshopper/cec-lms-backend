from flask import Blueprint, abort, jsonify, g
from pydantic import BaseModel

from cec_lms_backend import db
from cec_lms_backend.endpoints.auth import verify_empty, verify_json, verify_user

course = Blueprint("course", __name__, url_prefix="/course/<int:course_id>")

@course.url_value_preprocessor
def verify_course_id(endpoint, values: dict):
    course_id = values.pop("course_id", None)
    if not db.courses.course_exists(course_id):
        abort(404)
    g.course_id = course_id


@course.get("/progress")
@verify_user()
@verify_empty
def get_progress():
    progress = db.courses.get_progress(g.user_id, g.course_id)
    return jsonify(progress)

class DeleteProgressSchema(BaseModel):
    user_id: int
@course.delete("/progress")
@verify_user(roles=["admin"])
@verify_json(DeleteProgressSchema)
def delete_progress():
    db.courses.delete_progress(g.body["user_id"], g.course_id)
    return jsonify(success=True), 200

@course.get("/cursor")
@verify_user
@verify_empty
def get_cursor():
    cursor = db.courses.get_cursor(g.user_id, g.course_id)
    return jsonify(cursor), 200

@course.get("/content")
@verify_empty
def get_content():
    content = db.courses.get_content(g.course_id)
    return jsonify(content), 200