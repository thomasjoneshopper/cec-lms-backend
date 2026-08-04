import json
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
    with open("img_url_map.json") as f: img_map = json.load(f)
    with open("old_names.json") as f: old_names = json.load(f)
    
    with connect() as connection:
        cursor = connection.cursor()

        # Insert Course
        print(f"Inserting course \"{data["title"]}\"")
        cursor.execute(
            """
            INSERT INTO Courses (title_en, title_es)
            OUTPUT INSERTED.course_id 
            VALUES (?, ?)
            """, data["title"], data["titleEs"]
        )
        course_id = cursor.fetchval()

        # Insert Modules and Paragraphs
        quizzes = []
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
                if "image" in p:
                    old_url = p["image"]
                    if old_url.split(":")[0] == "__img":
                        old_url = old_names[old_url.split(":")[1]]
                    p["image"] = img_map.get(old_url, "")

                cursor.execute(
                    """
                    INSERT INTO dbo.Paragraphs (
                        module_id, ordinal,
                        title_en, title_es,
                        body_en, body_es,
                        extras_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, module_id,  j, 
                    p.pop("tagline"), p.pop("taglineEs"), 
                    p.pop("text"), p.pop("textEs"),
                    json.dumps(p)
                )
                

            if "quiz" in m:
                print(f"\b\b\b\b100%", end="", flush=True)
                quizzes.append({
                    "description": (course_id, module_id, 90), 
                    "questions": (q for s in m["quiz"]["sections"] for q in s["questions"]),
                    "length": sum(len(s["questions"]) for s in m["quiz"]["sections"])
                })
            
            print()

        quizzes.append({
            "description": (course_id, None, 80), 
            "questions": data["finalQuiz"],
            "length": len(data["finalQuiz"])
        })

        for i, quiz in enumerate(quizzes):
            print(f"    Inserting quiz {i}:     0%", end="", flush=True)
            cursor.execute(
                """
                INSERT INTO dbo.Quizzes (
                    course_id, 
                    module_id, 
                    passing_score 
                )
                OUTPUT INSERTED.quiz_id
                VALUES (?, ?, ?)
                """, quiz["description"]
            )
            quiz_id = cursor.fetchval()
            for j, q in enumerate(quiz["questions"]):
                print(f"\b\b\b\b{100*(j+1)/quiz["length"]:3.0f}%", end="", flush=True)
                cursor.execute(
                    """
                    INSERT INTO dbo.Questions (
                        quiz_id, ordinal,
                        body_en, body_es,
                        hint_en, hint_es
                    )
                    OUTPUT INSERTED.question_id
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    quiz_id, j,
                    q["question"], q["questionEs"],
                    q["hint"], q["hintEs"]
                )
                question_id = cursor.fetchval()
                cursor.executemany(
                    """
                    INSERT INTO dbo.Answers (
                        question_id,
                        body_en, body_es,
                        correct
                    )
                    VALUES (?, ?, ?, ?)
                    """, (
                        (question_id, q["options"][k], q["optionsEs"][k], k == q["correct"]) 
                        for k in range(len(q["options"]))
                    )
                )
            print()

        connection.commit()
