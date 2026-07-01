from cec_lms_backend import db

with open("../cec-loto-lms/lessonData.json") as f: db.load_content(f)