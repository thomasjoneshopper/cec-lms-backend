from cec_lms_backend.db.connection import connect
from cec_lms_backend.db.courses import ensure_course_progress

context_cache = {}

def load_cache():
    global context_cache
    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT M.course_id, P.module_id, P.paragraph_id
            FROM dbo.Paragraphs AS P
            JOIN dbo.Modules AS M ON P.module_id = M.module_id
            """
        )
        context_cache = {row.paragraph_id: (row.course_id, row.module_id) for row in cursor}

def update_completion(user_id: int, paragraph_id: int):
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
        
        course_id, module_id = context_cache[paragraph_id]
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