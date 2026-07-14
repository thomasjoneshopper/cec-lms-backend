from cec_lms_backend.app import create_app
from cec_lms_backend.db.connection import ping

assert ping()