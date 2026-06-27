import json
import os
import tempfile
from typing import Any, Dict


def read_file_content(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def save_build_json_file(
    build_json: Dict[str, Any], output_dir: str, build_number: int
) -> None:
    """Save build JSON to disk atomically."""

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"run_{build_number}.json")

    fd, tmp_path = tempfile.mkstemp(
        prefix=f"run_{build_number}_", dir=output_dir, text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(build_json, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, filename)
        logger.info("JSON saved: %s", filename)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
