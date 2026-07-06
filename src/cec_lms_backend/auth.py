from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Blueprint, g, request, jsonify
import jwt

from . import config
from . import db


def create_token(user_id):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=config.JWT_TTL_SECONDS)
    }

    return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGO)
    
def verify_session(f):
    """
    Decodes the jwt stored in httpOnly cookie. 
    Will add `user_id` attribute to `g` object if successful, or return 401 if not
    """
    @wraps(f)
    def wrapper():
        cookie = request.cookies.get(config.SESSION_COOKIE)
        try:
            claims = jwt.decode(
                jwt=cookie, key=config.JWT_SECRET, algorithms=[config.JWT_ALGO],
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


auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.post("/login")
def login():
    body: dict = request.get_json()
    if not isinstance(body, dict) or not {"name", "employee_number"} <= set(body):
        return jsonify(error="need name and employee_number"), 400
    
    # upsert user
    # get user_id
    user_id = 1

    response = jsonify(authenticated=True)
    response.set_cookie(
        config.SESSION_COOKIE, 
        create_token(user_id), 
        max_age=config.JWT_TTL_SECONDS, 
        httponly=True
    )
    return response

@auth.post("/logout")
@verify_session
def logout():
    response = jsonify(authenticated=False)
    response.delete_cookie(config.SESSION_COOKIE, httponly=True)
    return response

@auth.get("/me")
@verify_session
def me():
    return f"user information for user {g.user_id}", 200
