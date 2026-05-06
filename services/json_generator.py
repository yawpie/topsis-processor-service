import json
from io import BytesIO
from typing import Any


def generate_json_file_in_memory(data: Any, filename: str = "data.json") -> tuple[str, BytesIO]:
    """
    Generate file JSON di memory.
    Return:
    - filename
    - file object BytesIO
    """

    json_bytes = json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    file_obj = BytesIO(json_bytes)
    file_obj.seek(0)

    return filename, file_obj