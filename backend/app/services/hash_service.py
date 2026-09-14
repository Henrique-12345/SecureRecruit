import hashlib
from pathlib import Path
from typing import BinaryIO


def calculate_file_hash(file_obj: BinaryIO | bytes | Path) -> str:
    """Calculate SHA-256 hash of a file or bytes payload."""
    digest = hashlib.sha256()

    if isinstance(file_obj, Path):
        with file_obj.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    if isinstance(file_obj, bytes):
        digest.update(file_obj)
        return digest.hexdigest()

    position = file_obj.tell()
    file_obj.seek(0)
    for chunk in iter(lambda: file_obj.read(8192), b""):
        digest.update(chunk)
    file_obj.seek(position)
    return digest.hexdigest()


def verify_file_integrity(file_path: Path, expected_hash: str) -> tuple[str, bool]:
    current_hash = calculate_file_hash(file_path)
    return current_hash, current_hash == expected_hash
