from cec_lms_backend.db.connection import connect

def course_exists(course_id: int) -> bool:
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT (1) FROM dbo.Courses
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

def save_progress(user_id: int, course_id: int, module_id: int, paragraph_number: int) -> None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            IF NOT EXISTS (
                SELECT 1 FROM dbo.UserCourseProgress
                WHERE user_id = ?
                AND course_id = ?
            )
            BEGIN
                INSERT INTO dbo.UserCourseProgress (user_id, course_id)
                VALUES (?, ?)
            END
            """, user_id, course_id
        )

        cursor.execute(
            """
            UPDATE dbo.UserParagraphCompletion
            SET completion_time = SYSDATETIME()
            WHERE user_id = ?
            AND module_id ?
            AND paragraph_number ?
            """
        )

        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO dbo.UserParagraphCompletion (
                    user_id,
                    course_id,
                    module_id,
                    paragraph_number
                )
                VALUES (?, ?, ?, ?)
                """,
                user_id,
                course_id,
                module_id,
                paragraph_number
            )