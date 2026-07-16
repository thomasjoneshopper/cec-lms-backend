from pyodbc import Connection

from cec_lms_backend.db.connection import connect
from cec_lms_backend.db.utils import fetch_dict

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

def update_completion(user_id: int, course_id: int, module_id: int, paragraph_id: int):
    """
    does nothing if already complete
    creates usercourseprogress entry if necessary
    """
    
    with connect() as connection:
        # Check if paragraph already completed
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT 1 FROM dbo.UserParagraphCompletion
            WHERE user_id = ?
            AND paragraph_id = ?
            """,
            user_id,
            paragraph_id
        )

        if cursor.fetchval() == 1:
            return # already completed
        
        ensure_course_progress(connection, user_id, course_id)
        
        # save paragraph completion
        cursor.execute(
            """
            INSERT INTO dbo.UserParagraphCompletion (
                user_id,
                course_id,
                module_id,
                paragraph_id
            )
            VALUES (?, ?, ?, ?)
            """,
            user_id,
            course_id,
            module_id,
            paragraph_id
        )

        connection.commit()

def get_last_attempt(user_id: int, course_id: int, quiz_id: int):
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT TOP 1 attempt_id, correct_answers, submission_time
            FROM dbo.UserQuizAttempts
            ORDER BY submission_time DESC
            """
        )

        return fetch_dict(cursor)

def update_attempts(user_id: int, course_id: int, quiz_id: int, correct_answers: int) -> int:
    """
    creates new attempt entry
    creates usercourseprogress entry if necessary
    """
    
    with connect() as connection:
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