from pyodbc import Connection

from cec_lms_backend.db.connection import connect

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
            LEFT JOIN dbo.UserParagraphCompletion AS c
            ON p.paragraph_id = c.paragraph_id
            AND c.user_id = ?
            WHERE c.course_id = ?
            AND c.paragraph_id IS NULL
            """, user_id, course_id
        )
        return (cursor.fetchone() is None)
    
def quizzes_passed(user_id: int, course_id: int) -> bool:
    with connect() as connection:
        # get ids of all quizzes that have not been passed
        cursor = connection.execute(
            """
            SELECT q.quiz_id
            FROM dbo.Quizzes AS q
            LEFT JOIN dbo.UserQuizAttempts AS a
            ON q.quiz_id = a.quiz_id
            AND a.user_id = ?
            AND a.correct_answers >= q.passing_score
            WHERE q.course_id = ?
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

def get_progress(user_id: int, course_id: int) -> dict:
    with connect() as connection:
        cursor = connection.cursor()
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
            if modules.get(mid):
                modules[mid].append(pid)
            else: 
                modules[mid] = [pid]

    return {
        "course_id": course_id,
        "modules": [
            {
                "module_id": key,
                "completed_paragraphs": value
            }
            for key, value in modules.items()
        ]
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