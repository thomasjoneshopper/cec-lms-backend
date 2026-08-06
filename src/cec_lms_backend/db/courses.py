from pyodbc import Connection

from cec_lms_backend.db.connection import connect
from cec_lms_backend.db.utils import fetch_dict

def course_exists(course_id: int) -> bool:
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT 1 FROM dbo.Courses
            WHERE course_id = ?
            """, course_id
        )
        return bool(cursor.fetchval())

def paragraphs_complete(user_id: int, course_id: int) -> bool:
    with connect() as connection:
        # get ids of all incomplete paragraphs
        cursor = connection.execute(
            """
            SELECT p.paragraph_id 
            FROM dbo.Paragraphs AS p
            JOIN dbo.Modules AS m
            ON p.module_id = m.module_id
            LEFT JOIN dbo.UserParagraphCompletion AS c
            ON p.paragraph_id = c.paragraph_id
            AND c.user_id = ?
            WHERE m.course_id = ?
            AND c.completion_time IS NULL
            """, user_id, course_id
        )
        return (cursor.fetchone() is None)
    
def module_quizzes_passed(user_id: int, course_id: int) -> bool:
    with connect() as connection:
        # get ids of all quizzes that have not been passed
        cursor = connection.execute(
            """
            SELECT q.quiz_id
            FROM dbo.Quizzes AS q
            LEFT JOIN dbo.UserQuizAttempts AS a
            ON q.quiz_id = a.quiz_id
            AND a.user_id = ?
            AND a.pass
            WHERE q.course_id = ?
            AND q.module_id IS NOT NULL
            AND a.attempt_id IS NULL
            """, user_id, course_id
        )
        return (cursor.fetchone() is None)

def ensure_course_progress(connection: Connection, user_id: int, course_id: int):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT 1 FROM dbo.UserCourseProgress
        WHERE user_id = ?
        AND course_id = ?
        """, user_id, course_id
    )

    if cursor.fetchval():
        return

    cursor.execute(
        """
        INSERT INTO dbo.UserCourseProgress (user_id, course_id)
        VALUES (?, ?)
        """, user_id, course_id
    )

    connection.commit()

def get_progress(user_id: int, course_id: int) -> dict | None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT 1 FROM dbo.UserCourseProgress
            WHERE user_id = ? and course_id = ?
            """, user_id, course_id
        )
        if not cursor.fetchval(): return None

        cursor.execute(
            """
            SELECT module_id, paragraph_id
            FROM dbo.UserParagraphCompletion
            WHERE user_id = ? AND course_id = ?
            ORDER BY module_id
            """, user_id, course_id
        )

        modules = {}
        for mid, pid in cursor:
            modules[mid] = modules.get(mid, []) + [pid]

        cursor.execute(
            """
            SELECT  q.quiz_id, q.module_id, MAX(CAST(a.pass AS INT)) AS pass
            FROM dbo.Quizzes AS q
            JOIN dbo.UserQuizAttempts AS a
            ON q.quiz_id = a.quiz_id
            AND a.user_id = ?
            WHERE q.course_id = ?
            GROUP BY q.quiz_id, q.module_id
            """, user_id, course_id
        )

        quizzes = [{
            "quiz_id": qid,
            "module_id": mid,
            "pass": pass_
        } for qid, mid, pass_ in cursor]

    return {
        "course_id": course_id,
        "modules": [
            {
                "module_id": key,
                "completed_paragraphs": value
            }
            for key, value in modules.items()
        ],
        "quizzes": quizzes
    }

def delete_progress(user_id: int, course_id: int):
    with connect() as connection:
        connection.execute(
            """
            DELETE FROM dbo.UserCourseProgress
            WHERE user_id = ?
            AND course_id = ?
            """, user_id, course_id
        )

        connection.commit()

def get_cursor(user_id: int, course_id: int) -> dict | None:
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT active_module, active_paragraph
            FROM dbo.UserCourseProgress
            WHERE user_id = ? AND course_id = ?
            """, user_id, course_id
        )
        return fetch_dict(cursor)