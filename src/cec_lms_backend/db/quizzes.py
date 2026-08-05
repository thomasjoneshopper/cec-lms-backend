from cec_lms_backend.db.connection import connect
from cec_lms_backend.db.utils import fetch_dict
from cec_lms_backend.db.courses import ensure_course_progress

quiz_cache = dict()
answer_cache = dict()
"""
1. check if all questions answered
answers -> questions
cache[quiz_id]["questions"] == questions

2. calculate score
score = 100*sum(q["correct"] for q in questions)//len(questions)
pass_ = score >= cache[quiz_id]["passing_score"]

3. create db entries


need to cache:
 - answers -> questions
 - answer -> correct
 - quiz -> all questions
 - quiz -> context
 - quiz -> passing_score
"""


def load_cache(): 
    global quiz_cache
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT quiz_id, course_id, module_id, passing_score
            FROM dbo.Quizzes
            """
        )

        quiz_cache = {
            qid: {
                "course_id": cid,
                "module_id": mid,
                "passing_score": score,
                "question_count": 0
            }

            for qid, cid, mid, score in cursor
        }

        cursor = connection.execute(
            """
            SELECT q.quiz_id, q.question_id, a.answer_id, a.correct
            FROM dbo.Answers AS a
            JOIN dbo.Questions AS q
            ON a.question_id = q.question_id
            """
        )

        for quiz_id, question_id, answer_id, correct in cursor:
            quiz_cache[quiz_id]["question_count"] += 1
            answer_cache[answer_id] = {
                "quiz_id": quiz_id,
                "question_id": question_id,
                "correct": correct
            }

def is_final(quiz_id: int) -> bool:
    return quiz_cache[quiz_id]["module_id"] is None

def get_last_attempt(user_id: int, quiz_id: int):
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT TOP 1 attempt_id, quiz_id, pass, submission_time
            FROM dbo.UserQuizAttempts
            WHERE user_id = ?
            AND quiz_id = ?
            ORDER BY submission_time DESC
            """, user_id, quiz_id
        )

        return fetch_dict(cursor)

def is_pass(quiz_id: int, answers: list[int]) -> bool | None:
    """
    Grades quiz from answers.
    Returns `True` if passed, `False` if failed, `None` if invalid
    """

    questions_answered = set()
    correct = 0
    for a in answers:
        if answer_cache[a]["quiz_id"] != quiz_id: 
            return None
        questions_answered.add(a)
        correct += answer_cache[a]["correct"]

    if len(questions_answered) != quiz_cache[quiz_id]["question_count"]:
        return None
    score = 100*correct // quiz_cache[quiz_id]["question_count"]
    return (score >= quiz_cache[quiz_id]["passing_score"])



def create_attempt(user_id: int, quiz_id: int, pass_: int, answers: list[int]) -> int:
    """
    creates attempt entry and answer selection entries
    creates `UserCourseProgress` entry if necessary
    """

    with connect() as connection:
        course_id = quiz_cache[quiz_id]["course_id"]
        ensure_course_progress(connection, user_id, course_id)
        cursor = connection.execute(
            """
            INSERT INTO dbo.UserQuizAttempts (
                user_id,
                course_id,
                quiz_id,
                pass
            )
            OUTPUT INSERTED.attempt_id
            VALUES (?, ?, ?, ?)
            """,
            user_id,
            course_id,
            quiz_id,
            pass_ == 1
        )
        attempt_id = cursor.fetchval()

        cursor.executemany(
            """
            INSERT INTO dbo.UserAnswerSelections (
                attempt_id,
                quiz_id,
                question_id,
                answer_id
            )
            VALUES (?, ?, ?, ?)
            """, map(
                lambda a: (
                    attempt_id, 
                    quiz_id, 
                    answer_cache[a]["question_id"], 
                    a
                ), 
                answers
            )
        )

        connection.commit()
    
    return attempt_id