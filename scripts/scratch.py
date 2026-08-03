import json
import time


with open("../../cec-loto-lms/lessonData.json") as f:
    data = json.load(f)


paragraphs = [set(p.keys()) for m in data["modules"] for p in m["paragraphs"]]
all_keys = set.union(*paragraphs)

map = {}
for key in all_keys:
    bitmap = 0
    bit = 1
    for p in paragraphs:
        if key in p:
            bitmap |= bit
        bit *= 2
    map[bitmap] = map.get(bitmap, []) + [key]

print(*(f"{k:039_x}: {v}" for k,v in map.items()), sep="\n")

for bmp, l in map.items():
    print(f"{l[0]}: ", end="")
    for other in map:
        if bmp & other == 0:
            print(map[other][0], end=" ")
    print()



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
    
    
    


