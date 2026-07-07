from functools import wraps

from flask import g, request, jsonify
import jwt
from pydantic import BaseModel, ValidationError

from . import config
from . import db


def verify_user(roles=("reader","admin")):
    """
    Decodes the jwt stored in httpOnly cookie, and verifies that `user_id` is in database.
    Adds `g.user_id` attribute if decoding successful, returns `401 Unauthorized` if not.
    """
    def verify_user_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cookie = request.cookies.get(config.SESSION_COOKIE)
            if not cookie:
                return jsonify(error="Authentication required"), 401
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
            g.user_role = db.users.get_role(g.user_id)
            if g.user_role not in roles:
                return jsonify(error="Insufficient permissions"), 403

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
            except ValidationError as e:
                errors = [{
                    "field": ".".join(map(str, err["loc"])),
                    "message": err["msg"]
                } for err in e.errors()]
                return jsonify(errors=errors), 400
            except Exception as e:
                return jsonify(error=str(e)), 400
            g.body = obj.model_dump()
            return f(*args, **kwargs)
        
        return wrapper
    
    return verify_json_decorator

def verify_empty(f):
    """
    Verified that request body is empty, returning `400 Bad Request` if not.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.get_data():
            return jsonify(error="Request body must be empty"), 400
        return f(*args, **kwargs)
    
    return wrapper

