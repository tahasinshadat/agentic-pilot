"""List all files and folders in a directory."""

import os
from typing import Dict, Any


def list_files(directory_path: str = ".") -> Dict[str, Any]:
    """
    List all files and folders in directory.

    Parameters
    ----------
    directory_path:
        Path to the directory to list (defaults to current directory)

    Returns
    -------
    dict
        Status, message, and list of files
    """
    try:
        path_to_list = directory_path or '.'

        if not isinstance(path_to_list, str):
            return {"status": "error", "message": "Invalid directory path."}

        if not os.path.isdir(path_to_list):
            return {"status": "error", "message": f"'{path_to_list}' is not a directory."}

        files = os.listdir(path_to_list)

        return {
            "status": "success",
            "message": f"Found {len(files)} items in '{path_to_list}'",
            "files": files,
            "directory_path": path_to_list
        }

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
