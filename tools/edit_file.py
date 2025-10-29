"""Append content to an existing file."""

import os
from typing import Dict, Any


def edit_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Append content to an existing file.

    Parameters
    ----------
    file_path:
        Path to the file to edit
    content:
        Content to append to the file

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not file_path or not isinstance(file_path, str):
            return {"status": "error", "message": "Invalid file path."}

        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File '{file_path}' does not exist."}

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}")

        return {"status": "success", "message": f"Appended to file: '{file_path}'"}

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
