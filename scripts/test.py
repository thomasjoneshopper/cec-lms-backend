import time

import requests

from cec_lms_backend import db
from cec_lms_backend.db import paragraphs as p, quizzes as q
from cec_lms_backend.db.connection import connect

DOMAIN = "http://127.0.0.1:5000"

class AuthenticatedSession:
    default_creds = {
        "employee_number": "0TA160000",
        "full_name": "John Doe"
    }

    def __init__(self, login_creds=default_creds):
        self.login_creds = login_creds
    
    def __enter__(self):
        print("logging in ...", end="", flush=True)
        self.s = requests.sessions.session()
        self.s.post(DOMAIN+"/auth/login", json=self.login_creds)
        print(" done")
        return self.s
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("logging out ...", end="", flush=True)
        self.s.post(DOMAIN+"/auth/logout")
        if exc_type: print(exc_type)
        print(" done")
        return False

def print_response(r: requests.Response):
    print(f"{r.request.method} {r.url}")
    print(f"    {r.status_code} {r.reason}")
    for key, value in r.headers.items():
        print(f"    {key}: {value}")
    print()
    for line in r.text.split("\n"):
        print(f"    {line}")
    print()



def test_api():
    with AuthenticatedSession() as s:

        # for i in range(1,123):
        #     r = s.post(f"{DOMAIN}/paragraph/{i}/completion")
        #     print(f"{i:>3}: {r.status_code} {r.reason}")

        # for i in range(1,5):
        #     r = s.post(f"{DOMAIN}/quiz/{i}/attempts", json={"correct_answers": 10})
        #     print(f"{i:>3}: {r.status_code} {r.reason}")

        # r = s.post(f"{DOMAIN}/quiz/{5}/attempts", json={"correct_answers": 27})
        # print(f"{5:>3}: {r.status_code} {r.reason}")
        
        r = s.get(f"{DOMAIN}/course/1/progress")
        print_response(r)


def test_load_content():
    with open("/home/thomas/cec-loto-lms/lessonData.json") as f: 
        db.utils.load_content(f)

def test_pooling(n: int = 100):
    spids = {}
    start = time.perf_counter()
    for _ in range(n):
        with connect() as connection:
            spid = connection.execute("SELECT @@SPID").fetchval()
            spids[spid] = spids.get(spid, 0) + 1
    end = time.perf_counter()
    print(f"\nConnected {n} times in {end-start : .0f} seconds ({(end-start)/n:.3f} seconds per connection)")
    print(f"SPIDs:")
    print(*(f"{key:>4}: {value:>3}" for key,value in spids.items()), sep="\n")


if __name__ == "__main__":
    test_load_content()

    # with AuthenticatedSession() as s:
    #     r = s.put(f"{DOMAIN}/quiz/5/attempts", json={"correct_answers":5})
    #     print_response(r)
