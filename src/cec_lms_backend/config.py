from dotenv import load_dotenv
from os import environ

load_dotenv()

CONNECTION_STRING = environ["CONNECTION_STRING"]
JWT_SECRET = environ["JWT_SECRET"]
JWT_ALGO = "HS256"
JWT_TTL_SECONDS = 30 * 24 * 3600
SESSION_COOKIE = "session_id"

IMG_BASE = "/image"
