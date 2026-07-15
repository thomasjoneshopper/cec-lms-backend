import requests
from cec_lms_backend import db

DOMAIN = "http://127.0.0.1:5000"

class AuthenticatedSession:
    default_creds = {
        "employee_number": "0TA160000",
        "full_name": "John Doe"
    }

    def __init__(self, login_creds=default_creds):
        self.login_creds = login_creds
    
    def __enter__(self):
        self.s = requests.sessions.session()
        self.s.post(DOMAIN+"/auth/login", json=self.login_creds)
        return self.s
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.s.post(DOMAIN+"/auth/logout")
        if exc_type: print(exc_type)
        return False

def print_response(r: requests.Response):
    print(f"{r.url}")
    print(f"    {r.status_code} {r.reason}")
    for key, value in r.headers.items():
        print(f"    {key}: {value}")
    print()
    for line in r.text.split("\n"):
        print(f"    {line}")
    print()



def test_api():
    with AuthenticatedSession() as s:
        r = s.post(f"{DOMAIN}/paragraph/{1}/completion")
        print_response(r)


def test_load_content():
    with open("/home/thomas/cec-loto-lms/lessonData.json") as f: 
        db.utils.load_content(f)


if __name__ == "__main__":
    test_api()