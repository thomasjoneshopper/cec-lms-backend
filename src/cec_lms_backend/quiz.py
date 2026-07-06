from flask import Blueprint, g, request, jsonify

from .auth import verify_user

quiz = Blueprint("quiz", __name__, url_prefix="/quiz/<int:quiz_id>")

@quiz.url_value_preprocessor
def verify_quiz_id(endpoint, values: dict):
    quiz_id = values.pop("quiz_id", None)
    # verify quiz exists in db
    g.quiz_id = quiz_id

@quiz.get("/attempt")
@verify_user
def get_attempt():
    return f"reading last attempt of quiz {g.quiz_id} for user {g.user_id}\n", 200

@quiz.post("/attempt")
@verify_user
def post_attempt():
    return f"creating quiz {g.quiz_id} attempt for user {g.user_id}\n", 200

