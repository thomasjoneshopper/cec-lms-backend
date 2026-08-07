import json

from pyodbc import Connection

from cec_lms_backend.config import IMG_BASE
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
            SELECT  q.quiz_id, MAX(CAST(a.pass AS INT)) AS pass
            FROM dbo.Quizzes AS q
            JOIN dbo.UserQuizAttempts AS a
            ON q.quiz_id = a.quiz_id
            AND a.user_id = ?
            WHERE q.course_id = ?
            GROUP BY q.quiz_id
            """, user_id, course_id
        )

        quizzes = [{
            "quiz_id": qid,
            "pass": bool(pass_)
        } for qid, pass_ in cursor]

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

def get_content(course_id: int) -> dict | None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT course_id, title_en, title_es
            FROM dbo.Courses
            WHERE course_id = ?
            """, course_id
        )
        course_content = fetch_dict(cursor)
        if course_content is None: return None
        
        cursor.execute(
            """
            SELECT 
                m.course_id, m.module_id, m.ordinal AS m_ordinal,
                m.title_en AS m_title_en, m.title_es AS m_title_es,
                p.paragraph_id, p.ordinal AS p_ordinal, 
                p.title_en AS p_title_en, p.title_es AS p_title_es,
                p.body_en AS p_body_en, p.body_es AS p_body_es, p.extras_json AS p_extras_json
            FROM dbo.Modules AS m
            JOIN dbo.Paragraphs AS p 
            ON m.module_id = p.module_id
            WHERE m.course_id = ?
            ORDER BY m.ordinal, p.ordinal
            """, course_id
        )

        modules = dict()
        course_content["modules"] = []
        for row in cursor:
            module = modules.get(row.module_id)
            if module is None:
                module = {
                    "module_id": row.module_id,
                    "ordinal": row.m_ordinal,
                    "title_en": row.m_title_en,
                    "title_es": row.m_title_es,
                    "paragraphs": []
                }
                modules[row.module_id] = module
                course_content["modules"].append(module)

            extras = json.loads(row.p_extras_json)
            if "image" in extras:
                extras["image"] = f"{IMG_BASE}/{extras["image"]}"

            module["paragraphs"].append({
                "paragraph_id": row.paragraph_id,
                "ordinal": row.p_ordinal,
                "title_en": row.p_title_en,
                "title_es": row.p_title_es,
                "body_en": row.p_body_en,
                "body_es": row.p_body_es,
                "extras": extras
            })

        cursor.execute(
            """
            SELECT 
                qz.course_id, qz.module_id, qz.quiz_id, qz.passing_score,
                qs.question_id, qs.ordinal, 
                qs.body_en AS qs_body_en, qs.body_es AS qs_body_es,
                qs.hint_en, qs.hint_es,
                a.answer_id, a.body_en AS a_body_en, a.body_es AS a_body_es
            FROM dbo.Quizzes AS qz
            JOIN dbo.Questions AS qs 
            ON qz.quiz_id = qs.quiz_id
            JOIN dbo.Answers AS a 
            ON qs.question_id = a.question_id
            WHERE qz.course_id = ?
            ORDER BY qs.quiz_id, qs.ordinal, a.answer_id
            """, course_id
        )

        quizzes = dict()
        questions = dict()
        for row in cursor:
            quiz = quizzes.get(row.quiz_id)
            if quiz is None:
                quiz = {
                    "quiz_id": row.quiz_id,
                    "passing_score": row.passing_score,
                    "questions": []
                }

                if row.module_id is not None:
                    module = modules.get(row.module_id)
                    if module is None: continue
                    module["quiz"] = quiz
                else:
                    course_content["final"] = quiz
                quizzes[row.quiz_id] = quiz

            question = questions.get(row.question_id)
            if question is None:
                question = {
                    "question_id": row.question_id,
                    "ordinal": row.ordinal,
                    "body_en": row.qs_body_en,
                    "body_es": row.qs_body_es,
                    "hint_en": row.hint_en,
                    "hint_es": row.hint_es,
                    "answers": []
                }
                quiz["questions"].append(question)
                questions[row.question_id] = question

            question["answers"].append({
                "answer_id": row.answer_id,
                "body_en": row.a_body_en,
                "body_es": row.a_body_es
            })

        return course_content

