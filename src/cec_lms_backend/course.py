from flask import Blueprint, g, request, jsonify

from .auth import verify_user

course = Blueprint("course", __name__, url_prefix="/course/<int:course_id>")

@course.url_value_preprocessor
def verify_course_id(endpoint, values: dict):
    course_id = values.pop("course_id", None)
    # verify course exists in db
    g.course_id = course_id

@course.get("/progress")
@verify_user()
def get_progress():
    return f"reading progress for user {g.user_id} in course {g.course_id}\n", 200

@course.post("/progress")
@verify_user()
def post_progress():
    return f"updating progress for user {g.user_id} in course {g.course_id}\n", 200

@course.delete("/progress")
@verify_user(roles=("admin",)) # should require admin
def delete_progress():
    return f"deleting progress for user {g.user_id} in course {g.course_id}\n", 200



    