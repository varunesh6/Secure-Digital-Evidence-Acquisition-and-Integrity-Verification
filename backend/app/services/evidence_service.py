import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"pdf", "txt", "csv", "jpg", "png", "log"}


def compute_sha256(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def allowed_file(filename):
    if not filename:
        return False
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage, storage_root):
    if not file_storage or not file_storage.filename:
        raise ValueError("No file selected.")

    filename = secure_filename(file_storage.filename)
    if not filename:
        raise ValueError("Invalid filename.")

    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("File type is not allowed for evidence intake.")

    storage_dir = Path(storage_root)
    storage_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    target_path = storage_dir / unique_name
    file_storage.save(str(target_path))
    return str(target_path), unique_name


def sha256_for_bytes(data):
    return hashlib.sha256(data).hexdigest()


def ensure_storage_dirs(base_path):
    Path(base_path).mkdir(parents=True, exist_ok=True)
