"""Create a new folder at the specified path."""

import os
from typing import Dict, Any


def create_folder(folder_path: str) -> Dict[str, Any]:
    """
    Create a new folder.

    Parameters
    ----------
    folder_path:
        Path for the new folder

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not folder_path or not isinstance(folder_path, str):
            return {"status": "error", "message": "Invalid folder path."}

        if os.path.exists(folder_path):
            return {"status": "skipped", "message": f"Folder '{folder_path}' already exists."}

        os.makedirs(folder_path)
        return {"status": "success", "message": f"Created folder: '{folder_path}'"}

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
