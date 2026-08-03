import json
import math
from pyodbc import Cursor
from typing import TextIO

from cec_lms_backend.db.connection import connect

def fetch_dict(cursor: Cursor):
    row = cursor.fetchone()
    if row is None: return None
    columns = (column[0] for column in cursor.description)
    return dict(zip(columns, row))

def load_content(fp: TextIO):
    data = json.load(fp)
    with connect() as connection:
        cursor = connection.cursor()

        # Insert Course
        print("Inserting course")
        cursor.execute(
            """
            INSERT INTO Courses (title_en, title_es)
            OUTPUT INSERTED.course_id 
            VALUES (?, ?)
            """, data["title"], data["titleEs"]
        )
        course_id = cursor.fetchval()

        # Insert Modules, Paragraphs, and Quizzes
        for i, m in enumerate(data["modules"]):
            print(f"    Inserting module {i}:   0%", end="", flush=True)
            cursor.execute(
                """
                INSERT INTO dbo.Modules (course_id, ordinal, title_en, title_es)
                OUTPUT INSERTED.module_id
                VALUES (?, ?, ?, ?)
                """,
                course_id, i, m["title"], m["titleEs"]
            )
            module_id = cursor.fetchval()

            p_count = len(m["paragraphs"]) + int("quiz" in m)
            for j, p in enumerate(m["paragraphs"]):
                print(f"\b\b\b\b{100*(j+1)/p_count:3.0f}%", end="", flush=True)
                cursor.execute(
                    """
                    INSERT INTO dbo.Paragraphs (
                        module_id,
                        ordinal,
                        tagline_en,
                        tagline_es,
                        body_en,
                        body_es,
                        extras_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, module_id,  j, 
                    p.pop("tagline"), p.pop("taglineEs"), 
                    p.pop("text"), p.pop("textEs"), json.dumps(p)
                )

            if "quiz" in m:
                print(f"\b\b\b\b100%", end="", flush=True)
                length = sum(len(s["questions"]) for s in m["quiz"]["sections"])
                cursor.execute(
                    """
                    INSERT INTO dbo.Quizzes (
                        course_id, 
                        module_id, 
                        passing_score, 
                        question_count
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    course_id,
                    module_id,
                    math.ceil(length*0.9),
                    length
                )
            print()


        # insert final
        print("    Inserting final")
        final_length = len(data["finalQuiz"])
        cursor.execute(
            """
            INSERT INTO dbo.Quizzes (
                course_id, 
                passing_score, 
                question_count
            )
            VALUES (?, ?, ?)
            """,
            course_id, 
            math.ceil(final_length*0.8), 
            final_length
        )
        connection.commit()
