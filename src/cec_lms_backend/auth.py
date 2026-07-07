from datetime import datetime, timedelta, timezone

from flask import Blueprint, g, jsonify
import jwt
from pydantic import BaseModel

from . import config
from . import db
from .utils import verify_json, verify_user, verify_empty


auth = Blueprint("auth", __name__, url_prefix="/auth")

class LoginSchema(BaseModel):
    employee_number: str
    full_name: str

def create_token(user_id):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=config.JWT_TTL_SECONDS)
    }

    return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGO)

@auth.post("/login")
@verify_json(LoginSchema)
def login():
    user_id = db.users.get_id(**g.body)
    response = jsonify(authenticated=True)
    response.set_cookie(
        config.SESSION_COOKIE, 
        create_token(user_id), 
        max_age=config.JWT_TTL_SECONDS, 
        httponly=True
    )
    return response

@auth.post("/logout")
@verify_user()
@verify_empty
def logout():
    response = jsonify(authenticated=False)
    response.delete_cookie(config.SESSION_COOKIE, httponly=True)
    return response

@auth.get("/me")
@verify_user()
@verify_empty
def me():
    user = db.users.get_entry(g.user_id)
    return jsonify(user), 200
