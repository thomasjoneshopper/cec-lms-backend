from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, g
import jwt
from pydantic import BaseModel

from cec_lms_backend import config, db
from cec_lms_backend.utils import verify_empty, verify_json, verify_user


auth = Blueprint("auth", __name__, url_prefix="/auth")

class LoginSchema(BaseModel):
    employee_number: str
    full_name: str

@auth.post("/login")
@verify_json(LoginSchema)
def login():
    response = jsonify(authenticated=True)

    user_id = db.users.get_id(**g.body)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=config.JWT_TTL_SECONDS)
    }
    
    response.set_cookie(
        key=config.SESSION_COOKIE, 
        value=jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGO), 
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
