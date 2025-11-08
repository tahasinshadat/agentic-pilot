"""Create a new file with content."""

import os
from typing import Dict, Any
from utils.path_validator import validate_file_path


def create_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Create a new file with specified content.

    Parameters
    ----------
    file_path:
        Path for the new file
    content:
        Content to write to the file

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not file_path or not isinstance(file_path, str):
            return {"status": "error", "message": "Invalid file path."}

        if os.path.exists(file_path):
            return {"status": "skipped", "message": f"File '{file_path}' already exists."}

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {"status": "success", "message": f"Created file: '{file_path}'"}

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
