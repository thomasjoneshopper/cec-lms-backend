import json
import time


with open("../cec-loto-lms/lessonData.json") as f:
    data = json.load(f)

questions = []
for m in data["modules"]:
    if "quiz" not in m: continue
    questions.extend(set(q.keys()) for s in m["quiz"]["sections"] for q in s["questions"])

fields = set.intersection(*questions)
for q in questions:
    if q != fields: print(q)

def loading():
    animation = "—\\|/"
    rps = 2
    times = [13, 9, 5, 9]
    times = [x/(sum(times) * rps) for x in times]

    i=0
    print()
    while True:
        print("\x1b[2A", end="")
        print(f"loading: ({animation[i]})")
        time.sleep(times[i])
        i = (i + 1) % len(animation)
    
    
    


