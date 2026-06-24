from datetime import datetime, timedelta, timezone
import db
from dotenv import load_dotenv
from flask import Flask, g, request, jsonify
from functools import wraps
import jwt
from markupsafe import escape
from os import environ


load_dotenv()
JWT_SECRET = environ["JWT_SECRET"]
JWT_ALGO = "HS256"
JWT_TTL_SECONDS = 30 * 24 * 3600
SESSION_COOKIE = "session_id"

app = Flask(__name__)

def create_token(user_id):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=JWT_TTL_SECONDS)
    }

    return jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGO)
    
def verify_session(f):
    """
    Decodes the jwt stored in httpOnly cookie. 
    Will add `user_id` attribute to `g` object if successful, or return 401 if not
    """
    @wraps(f)
    def wrapper():
        cookie = request.cookies.get(SESSION_COOKIE)
        try:
            claims = jwt.decode(
                jwt=cookie, key=JWT_SECRET, algorithms=[JWT_ALGO],
                options={"require": ["sub", "exp", "iat"]}
            )
        except jwt.ExpiredSignatureError:
            return jsonify(error="Token expired"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token"), 401
        except jwt.PyJWTError as e:
            # log this, shouldn't happen
            return jsonify(error=e), 401

        g.user_id = int(claims["sub"])
        return f()
    return wrapper


@app.post("/auth/login")
def login():
    body: dict = request.get_json()
    if not isinstance(body, dict) or not {"name", "employee_number"} <= set(body):
        return jsonify(error="need name and employee_number"), 400
    
    user_id = db.Users.find(**body)
    body.update({"last_sign_in": datetime.now(timezone.utc)})
    if user_id == -1:
        user_id = db.Users.create(**body)
    else:
        db.Users.update(user_id, **body)

    response = jsonify(authenticated=True)
    response.set_cookie(
        SESSION_COOKIE, 
        create_token(user_id), 
        max_age=JWT_TTL_SECONDS, 
        httponly=True
    )
    return response

@app.get("/auth/me")
@verify_session
def me():
    return db.Users.read(g.user_id), 200

@app.post("/auth/logout")
@verify_session
def logout():
    response = jsonify(authenticated=False)
    response.delete_cookie(SESSION_COOKIE, httponly=True)
    return response


@app.get("/progress")
def get_progress():
    pass