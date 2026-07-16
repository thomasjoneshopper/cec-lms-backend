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
    
def get_quiz_context(quiz_id: int) -> dict | None:
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT course_id, quiz_id FROM dbo.Quizzes
            WHERE quiz_id = ?
            """, quiz_id
        )

        return fetch_dict(cursor)

def get_paragraph_context(paragraph_id: int) -> dict | None:
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT M.course_id, P.module_id, P.paragraph_id
            FROM dbo.Paragraphs AS P
            JOIN dbo.Modules AS M ON P.module_id = M.module_id
            WHERE paragraph_id = ?
            """, paragraph_id
        )

        return fetch_dict(cursor)
