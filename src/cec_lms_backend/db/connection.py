import json
from os import environ
import struct
from typing import TextIO

from azure.identity import AzureCliCredential
from dotenv import load_dotenv
import pyodbc

from cec_lms_backend.config import CONNECTION_STRING


def db_connect() -> pyodbc.Connection:
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    
    token = (
        AzureCliCredential()
        .get_token("https://database.windows.net/.default")
        .token.encode("utf-16-le")
    )
    exptoken = struct.pack(f"<I{len(token)}s", len(token), token)

    connection = pyodbc.connect(
        CONNECTION_STRING,
        timeout=30,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: exptoken}
    )

    return connection

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
                "question_count": sum([len(s) for s in m["quiz"]["sections"]])
            })
    final_length = len(data["finalQuiz"])

    with db_connect() as connection:
        cursor = connection.cursor()

        # Insert Course
        cursor.execute("INSERT INTO Courses (name) VALUES (?)", title)
        course_id = cursor.execute("SELECT course_id FROM Courses WHERE name = ?", title).fetchone()[0]


        # Insert Modules
        cursor.executemany(
            """
            INSERT INTO dbo.Modules (course_id, name, number, paragraph_count)
            VALUES (?, ?, ?, ?)
            """,
            [[course_id] + [module[k] for k in ("name", "number", "paragraph_count")] for module in modules]
        )

        # Insert Quizzes
        cursor.execute("SELECT number, module_id FROM Modules")
        map = {number: id for number,id in cursor.fetchall()}
        cursor.executemany(
            """
            INSERT INTO Quizzes (course_id, module_id, passing_score, question_count)
            VALUES (?, ?, 90, ?)
            """,
            [(course_id, map[q["module_number"]], q["question_count"]) for q in quizzes]
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
