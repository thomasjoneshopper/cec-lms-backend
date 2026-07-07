import json
from typing import TextIO

from .connection import connect

def load_content(fp: TextIO):
    data = json.load(fp)
    title = data["title"]
    modules = []
    quizzes = []
    for m in data["modules"]:
        modules.append({"name": m["title"], "number": m["id"]-1, "paragraph_count": len(m["paragraphs"])})
        if "quiz" in m:
            quizzes.append({
                "module_number": m["id"]-1, 
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
        cursor.executemany(
            """
            INSERT INTO dbo.Modules (course_id, title, ordinal, paragraph_count)
            VALUES (?, ?, ?, ?)
            """,
            ((course_id, m["name"], m["number"], m["paragraph_count"]) for m in modules)
        )

        # Insert Quizzes
        cursor.execute("SELECT ordinal, module_id FROM Modules")
        map = {number: id for number,id in cursor.fetchall()}
        cursor.executemany(
            """
            INSERT INTO Quizzes (course_id, module_id, passing_score, question_count)
            VALUES (?, ?, 90, ?)
            """,
            ((course_id, map[q["module_number"]], q["question_count"]) for q in quizzes)
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