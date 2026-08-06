from flask import Blueprint, abort, jsonify, g
from pydantic import BaseModel

from cec_lms_backend.endpoints.auth import verify_user, verify_json, verify_empty
from cec_lms_backend import db

quiz = Blueprint("quiz", __name__, url_prefix="/quiz/<int:quiz_id>")

@quiz.url_value_preprocessor
def verify_quiz_id(endpoint, values: dict):
    g.quiz_id = values.pop("quiz_id", None)
    if g.quiz_id not in db.quizzes.quiz_cache: abort(404)

@quiz.get("/attempts")
@verify_user()
@verify_empty
def get_attempt():
    attempt = db.quizzes.get_last_attempt(g.user_id, g.quiz_id)
    return jsonify(attempt), 200

class AttemptSchema(BaseModel):
    answers: list[int]
@quiz.post("/attempts")
@verify_user()
@verify_json(AttemptSchema)
def post_attempt():
    pass_ = db.quizzes.is_pass(g.quiz_id, **g.body)
    if pass_ is None: abort(400)

    if db.quizzes.is_final(g.quiz_id):
        course_id = db.quizzes.context_cache[g.quiz_id][0]
        msgs = []
        if not db.courses.paragraphs_complete(g.user_id, course_id):
            msgs.append("Not all paragraphs have been completed.")
        if not db.courses.quizzes_passed(g.user_id, course_id):
            msgs.append("Not all quizzes have been passed.")
        if msgs:
            abort(403, " ".join(msgs))
        
        
    attempt_id = db.quizzes.create_attempt(g.user_id, g.quiz_id, pass_, **g.body)
    return {
        "attempt_id": attempt_id, 
        "pass": pass_
    }, 200
