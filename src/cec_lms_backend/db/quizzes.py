from cec_lms_backend.db.connection import connect
from cec_lms_backend.db.utils import fetch_dict
from cec_lms_backend.db.courses import ensure_course_progress

context_cache = {}

def load_cache(): 
    global context_cache
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT course_id, module_id, quiz_id
            FROM dbo.Quizzes
            """
        )
        context_cache = {row.quiz_id: (row.course_id, row.module_id) for row in cursor}

def is_final(quiz_id: int) -> bool:
    return context_cache[quiz_id][1] is None

def get_last_attempt(user_id: int, quiz_id: int):
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT TOP 1 attempt_id, correct_answers, submission_time
            FROM dbo.UserQuizAttempts
            WHERE user_id = ?
            AND quiz_id = ?
            ORDER BY submission_time DESC
            """, user_id, quiz_id
        )

        return fetch_dict(cursor)

def update_attempts(user_id: int, quiz_id: int, correct_answers: int) -> int:
    """
    creates new attempt entry
    creates `UserCourseProgress` entry if necessary
    """
    
    with connect() as connection:
        course_id = context_cache[quiz_id][0]
        ensure_course_progress(connection, user_id, course_id)
        cursor = connection.execute(
            """
            INSERT INTO dbo.UserQuizAttempts (
                user_id,
                course_id,
                quiz_id,
                correct_answers
            )
            OUTPUT INSERTED.attempt_id
            VALUES (?, ?, ?, ?)
            """,
            user_id,
            course_id,
            quiz_id,
            correct_answers
        )
        attempt_id = cursor.fetchval()
        connection.commit()
    
    return attempt_id