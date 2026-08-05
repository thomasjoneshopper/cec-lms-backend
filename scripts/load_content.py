import json

from cec_lms_backend.db.connection import connect

with open("/home/thomas/cec-loto-lms/lessonData.json") as f: data = json.load(f)
with open("img_url_map.json") as f: img_map = json.load(f)
with open("old_names.json") as f: old_names = json.load(f)


def insert_course(cursor, course):
    cursor.execute(
        """
        INSERT INTO Courses (title_en, title_es)
        OUTPUT INSERTED.course_id 
        VALUES (?, ?)
        """, course["title"], course["titleEs"]
    )
    return cursor.fetchval()

def insert_module(cursor, module, course_id, ordinal):
    cursor.execute(
        """
        INSERT INTO dbo.Modules (course_id, ordinal, title_en, title_es)
        OUTPUT INSERTED.module_id
        VALUES (?, ?, ?, ?)
        """,
        course_id, ordinal, module["title"], module["titleEs"]
    )
    return cursor.fetchval()

def insert_paragraph(cursor, paragraph, module_id, ordinal):
    paragraph = paragraph.copy()
    cursor.execute(
        """
        INSERT INTO dbo.Paragraphs (
            module_id, ordinal,
            title_en, title_es,
            body_en, body_es,
            extras_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, module_id, ordinal, 
        paragraph.pop("tagline"), paragraph.pop("taglineEs"), 
        paragraph.pop("text"), paragraph.pop("textEs"),
        json.dumps(p)
    )

def insert_quiz(cursor, quiz):
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
    return cursor.fetchval()

def insert_question(cursor, question, quiz_id, ordinal):
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
        quiz_id, ordinal,
        question["question"], question["questionEs"],
        question["hint"], question["hintEs"]
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
        """, ((
                question_id, 
                question["options"][k], 
                question["optionsEs"][k], 
                k == question["correct"]
            ) 
            for k in range(len(q["options"]))
        )
    )
    
if __name__ == "__main__":
    with connect() as connection:
        cursor = connection.cursor()

        print(f"Inserting course \"{data["title"]}\"")
        course_id = insert_course(cursor, data)

        quizzes = []
        for i, m in enumerate(data["modules"]):
            print(f"    Inserting module {i}:   0%", end="", flush=True)
            module_id = insert_module(cursor, m, course_id, i)

            p_count = len(m["paragraphs"]) + int("quiz" in m)
            for j, p in enumerate(m["paragraphs"]):
                print(f"\b\b\b\b{100*(j+1)/p_count:3.0f}%", end="", flush=True)
                if "image" in p:
                    old_url = p["image"]
                    if old_url.split(":")[0] == "__img":
                        old_url = old_names[old_url.split(":")[1]]
                    p["image"] = img_map.get(old_url, "")

                insert_paragraph(cursor, p, module_id, j)
                
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
            quiz_id = insert_quiz(cursor, quiz)
            
            for j, q in enumerate(quiz["questions"]):
                print(f"\b\b\b\b{100*(j+1)/quiz["length"]:3.0f}%", end="", flush=True)
                insert_question(cursor, q, quiz_id, j)
                
            print()

        connection.commit()
