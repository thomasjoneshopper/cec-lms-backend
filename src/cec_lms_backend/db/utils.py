import json
from pyodbc import Cursor
from typing import TextIO

from cec_lms_backend.db.connection import connect

def load_content(fp: TextIO):
    data = json.load(fp)
    title = data["title"]
    modules = []
    paragraphs = []
    quizzes = []
    for m in data["modules"]:
        ordinal = m["id"] - 1
        modules.append({"name": m["title"], "ordinal": ordinal})
        paragraphs.extend({"module_ordinal": ordinal, "ordinal": i} for i in range(len(m["paragraphs"])))
        if "quiz" in m:
            quizzes.append({
                "module_ordinal": ordinal, 
                "question_count": sum(len(s["questions"]) for s in m["quiz"]["sections"])
            })
    final_length = len(data["finalQuiz"])

    with connect() as connection:
        cursor = connection.cursor()

        # Insert Course
        cursor.execute(
            """
            INSERT INTO Courses (title)
            OUTPUT INSERTED.course_id 
            VALUES (?)
            """, title
        )
        course_id = cursor.fetchval()

        # Insert Modules
        map: dict[int, int] = {}
        for m in modules:
            cursor.execute(
                """
                INSERT INTO dbo.Modules (course_id, title, ordinal)
                OUTPUT INSERTED.module_id
                VALUES (?, ?, ?)
                """,
                course_id, 
                m["name"], 
                m["ordinal"]
            )
            map[m["ordinal"]] = cursor.fetchval()


        # Insert Paragraphs
        cursor.executemany(
            """
            INSERT INTO dbo.Paragraphs (module_id, ordinal)
            VALUES (?, ?)
            """, 
            ((map[p["module_ordinal"]], p["ordinal"]) for p in paragraphs)
        )

        # Insert Quizzes
        cursor.executemany(
            """
            INSERT INTO Quizzes (course_id, module_id, passing_score, question_count)
            VALUES (?, ?, 90, ?)
            """,
            ((course_id, map[q["module_ordinal"]], q["question_count"]) for q in quizzes)
        )

        # Insert Final
        cursor.execute(
            """
            INSERT INTO dbo.Quizzes (course_id, passing_score, question_count)
            VALUES (?, 80, ?)
            """,
            (course_id, final_length)
        )
        connection.commit()

def fetch_dict(cursor: Cursor):
    row = cursor.fetchone()
    if row is None: return None
    columns = (column[0] for column in cursor.description)
    return dict(zip(columns, row))
