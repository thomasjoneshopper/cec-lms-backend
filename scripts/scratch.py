import asyncio
import json

from cec_lms_backend.db.courses import ensure_course_progress
from cec_lms_backend.db.connection import connect

async def loading():
    animation = "—\\|/"
    rps = 3
    times = [13, 9, 5, 9]
    times = [x/(sum(times) * rps) for x in times]

    i=0
    print()
    while True:
        print("\x1b[1A\x1b[2K", end="")
        print(f"loading: ({animation[i]})")
        asyncio.sleep(times[i])
        i = (i + 1) % len(animation)
    



