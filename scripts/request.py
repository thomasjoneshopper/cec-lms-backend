import requests

DOMAIN = "http://127.0.0.1:5000"

def print_response(r: requests.Response):
    print(f"{r.url}")
    print(f"    {r.status_code} {r.reason}")
    for key, value in r.headers.items():
        print(f"    {key}: {value}")
    print()
    for line in r.text.split("\n"):
        print(f"    {line}")
    print()

def test_all_endpoints():
    with requests.sessions.session() as s:
        # auth
        login_creds = {
            "employee_number": "0000",
            "name": "test",
        }
        r = s.post(DOMAIN+"/auth/login", json=login_creds)
        print_response(r)

        r = s.get(DOMAIN+"/auth/me")
        print_response(r)

        # # course
        # r = s.get(DOMAIN+"/course/1/progress")
        # print_response(r)

        # r = s.post(DOMAIN+"/course/1/progress")
        # print_response(r)

        # r = s.delete(DOMAIN+"/course/1/progress")
        # print_response(r)

        # # quiz
        # r = s.get(DOMAIN+"/quiz/1/attempt")
        # print_response(r)

        # r = s.post(DOMAIN+"/quiz/1/attempt")
        # print_response(r)

        # auth logout
        r = s.post(DOMAIN+"/auth/logout")
        print_response(r)

if __name__ == "__main__":
    test_all_endpoints()
