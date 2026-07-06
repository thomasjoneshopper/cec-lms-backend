from functools import wraps

from flask import g, request, jsonify
import jwt
from pydantic import BaseModel, ValidationError

from . import config
from . import db


def verify_user(f):
    """
    Decodes the jwt stored in httpOnly cookie. 
    Adds `g.user_id` attribute if successful, returns 401 if not
    """
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
        if not db.users.exists(g.user_id):
            return jsonify(error="Insufficient permissions"), 403

        return f(*args, **kwargs)
    return wrapper

def verify_json(schema: type[BaseModel]):
    """
    Verifies that request body json matches `schema` using `pydantic`

    Adds `g.body` attribute if valid, returns 400 if not
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

