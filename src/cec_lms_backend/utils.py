from functools import wraps

from flask import g, request, jsonify
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
            error_message = None

            if not cookie:
                return jsonify(error="Authentication required"), 401
            try:
                if not cookie: raise ValueError
                claims = jwt.decode(
                    jwt=cookie, key=config.JWT_SECRET, algorithms=[config.JWT_ALGO],
                    options={"require": ["sub", "exp", "iat"]}
                )

            except ValueError: error_message = "Authentication required"
            except jwt.ExpiredSignatureError: error_message = "Token expired"
            except jwt.InvalidTokenError: error_message = "Invalid token"
            except jwt.PyJWTError as e: error_message = str(e)

            if error_message:
                return jsonify(
                    error="401 Unauthorized", 
                    message=error_message
                ), 401

            g.user_id = int(claims["sub"])
            g.user_role = db.users.get_role(g.user_id)
            if g.user_role not in roles:
                return jsonify(
                    error="403 Forbidden",
                    message="Insufficient permissions"
                ), 403

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
                return jsonify(
                    error="400 Bad Request",
                    details=[
                        {
                            "type": err["type"],
                            "field": ".".join(map(str, err["loc"])),
                            "message": err["msg"]
                        } for err in e.errors()
                    ]
                ), 400
            
            except Exception as e:
                return jsonify(error=str(e)), 400
            
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
            return jsonify(
                error="400 Bad Request",
                message="Request body must be empty"
            ), 400
        return f(*args, **kwargs)
    
    return wrapper
