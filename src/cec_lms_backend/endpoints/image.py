from importlib.resources import files

from flask import Blueprint, send_from_directory

from cec_lms_backend.endpoints.auth import verify_empty


IMG_DIR = files("cec_lms_backend") / "img"

image = Blueprint("image", __name__)
@image.get("/image/<path:filename>")
@verify_empty
def get_image(filename):
    return send_from_directory(IMG_DIR, filename)