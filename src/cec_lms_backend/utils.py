from functools import wraps

from flask import abort, jsonify, g, request
import jwt
from pydantic import BaseModel, ValidationError

from cec_lms_backend import config, db


def verify_user(roles=["reader","admin"]):
    """
    Decodes the jwt stored in httpOnly cookie, and verifies that `user_id` is in database.
    Adds `g.user_id` attribute if decoding successful, returns `401 Unauthorized` if not.
    """
    def verify_user_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cookie = request.cookies.get(config.SESSION_COOKIE)

            if not cookie: abort(401, "Authentication required")
            try:
                claims = jwt.decode(
                    jwt=cookie, key=config.JWT_SECRET, algorithms=[config.JWT_ALGO],
                    options={"require": ["sub", "exp", "iat"]}
                )
            except jwt.InvalidTokenError: abort(401, "Invalid token")
            except jwt.PyJWTError as e: abort(401, str(e))

            g.user_id = int(claims["sub"])
            g.user_role = db.users.get_role(g.user_id)
            if g.user_role not in roles: abort(403)

            return f(*args, **kwargs)
        return wrapper
    return verify_user_decorator

def verify_json(schema: type[BaseModel]):
    """
    Verifies that request body json matches `schema` using `pydantic`.
    Adds `g.body` attribute if valid, returns `400 Bad Request` if not.
    """

    def verify_json_decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                obj = schema.model_validate(request.get_json(), strict=True, extra="forbid")
            except ValidationError as error:
                return jsonify(
                    error="400 Bad Request",
                    details=[{
                        "field": ".".join(map(str, d["loc"])),
                        "message": d["msg"]
                    } for d in error.errors()]
                ), 400
            
            except Exception as e: abort(400, str(e))
            
            g.body = obj.model_dump()
            return f(*args, **kwargs)
        
        return wrapper
    
    return verify_json_decorator

def verify_empty(f):
    """
    Verifies that request body is empty, returning `400 Bad Request` if not.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.get_data():
            abort(400, "Request body must be empty")
        return f(*args, **kwargs)
    
    return wrapper
