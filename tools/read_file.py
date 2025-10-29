"""Read entire file content."""

import os
from typing import Dict, Any


def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read entire file content.

    Parameters
    ----------
    file_path:
        Path to the file to read

    Returns
    -------
    dict
        Status, message, and file content
    """
    try:
        if not file_path or not isinstance(file_path, str):
            return {"status": "error", "message": "Invalid file path."}

        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File '{file_path}' does not exist."}

        if not os.path.isfile(file_path):
            return {"status": "error", "message": f"'{file_path}' is not a file."}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "status": "success",
            "message": f"Read file: '{file_path}'",
            "content": content
        }

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
