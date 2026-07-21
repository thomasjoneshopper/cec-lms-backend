from flask import Blueprint, abort, jsonify, g
from pydantic import BaseModel

from cec_lms_backend.endpoints.auth import verify_user, verify_json, verify_empty
from cec_lms_backend import db

quiz = Blueprint("quiz", __name__, url_prefix="/quiz/<int:quiz_id>")

@quiz.url_value_preprocessor
def verify_quiz_id(endpoint, values: dict):
    quiz_id = values.pop("quiz_id", None)
    g.context = db.quizzes.context_cache.get(quiz_id)
    if not g.context:
        abort(404)

@quiz.get("/attempts")
@verify_user()
@verify_empty
def get_attempt():
    attempt = db.quizzes.get_last_attempt(g.user_id, *g.context)
    return jsonify(attempt), 200

class AttemptSchema(BaseModel):
    correct_answers: int
@quiz.post("/attempts")
@verify_user()
@verify_json(AttemptSchema)
def post_attempt():
    if db.quizzes.is_final(g.quiz_id):
        msg = ""
        if not db.courses.paragraphs_complete(g.user_id, g.course_id):
            msg += "Not all paragraphs have been completed. "
        if not db.courses.quizzes_passed(g.user_id, g.course_id):
            msg += "Not all paragraphs have been completed. "
        if msg:
            return jsonify(
                error="403 Forbidden",
                message=msg
            ), 403
        
    attempt_id = db.quizzes.update_attempts(g.user_id, g.quiz_id, **g.body)
    return jsonify(attempt_id=attempt_id), 200
