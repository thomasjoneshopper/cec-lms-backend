import requests
from requests_toolbelt.utils import dump

DOMAIN = "http://127.0.0.1:5000"

def print_response(r: requests.Response):
    print("Response:")
    print(f"    {r.status_code} {r.reason}")
    for key, value in r.headers.items():
        print(f"    {key}: {value}")
    print()
    for line in r.text.split("\n"):
        print(f"    {line}")
    print()

with requests.sessions.session() as s:
    login_creds = {
        "employee_number": "0000",
        "name": "test"
    }
    r = s.post(DOMAIN+"/auth/login", json=login_creds)
    print_response(r)

    r = s.get(DOMAIN+"/auth/me")
    print_response(r)

    r = s.post(DOMAIN+"/auth/logout")
    print_response(r)
