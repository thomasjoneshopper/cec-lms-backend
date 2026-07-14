import pyodbc

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

def get_progress(user_id: int, course_id: int) -> dict:
    # with connect() as connection:
    #     cursor = connection.execute(
    #         """
    #         SELECT * FROM dbo.UserCourseProgress
    #         WHERE user_id = ? AND course_id = ?
    #         """, user_id, course_id
    #     )

    return {
        "course_id": 1,
        "complete": True,
        "modules": [
            {
                "module_id": 1,
                "completed_paragraphs": [0,1,2,3]
            }
        ]
    }

def save_progress(user_id: int, paragraph_id: int) -> bool:
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

        if cursor.rowcount > 0:
            # already completed
            return True
        
        # check if paragraph exists
        cursor.execute(
            """
            SELECT P.module_id, M.course_id
            FROM dbo.Paragraphs AS P
            JOIN dbo.Modules AS M ON P.module_id = M.module_id
            WHERE paragraph_id = ?
            """, paragraph_id
        )

        if cursor.rowcount == 0:
            # paragraph does not exist
            return False
        
        module_id, course_id = cursor.fetchone()

        # Check if UserCourseProgress entry exists
        cursor.execute(
            """
            SELECT 1 FROM dbo.UserCourseProgress
            WHERE user_id = ?
            AND course_id = ?
            """, user_id, course_id
        )

        # Create new entry if does not exist
        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO dbo.UserCourseProgress (
                    user_id,
                    course_id,
                    active_module,
                    active_paragraph
                )
                VALUES (?, ?, ?, ?)
                """, user_id, course_id, module_id, paragraph_id
            )
        
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
        return True

