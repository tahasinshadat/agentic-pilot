"""Edit file content with multiple modes (append, replace, insert)."""

import os
from typing import Dict, Any, Optional


def edit_file(
    file_path: str,
    content: str,
    mode: str = "replace",
    line_number: Optional[int] = None
) -> Dict[str, Any]:
    """
    Edit a file with different modes.

    Parameters
    ----------
    file_path:
        Path to the file to edit
    content:
        Content to add/replace
    mode:
        Edit mode - "replace" (default), "append", or "insert"
        - replace: Replace entire file content (most common for AI editing)
        - append: Add content to end of file
        - insert: Insert content at specific line (requires line_number)
    line_number:
        Line number for insert mode (1-indexed)

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return {"status": "error", "message": "Invalid file path."}

        if not isinstance(content, str):
            return {"status": "error", "message": "Content must be a string."}

        if mode not in ["append", "replace", "insert"]:
            return {"status": "error", "message": f"Invalid mode '{mode}'. Use 'append', 'replace', or 'insert'."}

        if mode == "insert" and line_number is None:
            return {"status": "error", "message": "line_number required for insert mode."}

        # Check file exists (except for replace mode which can create)
        if mode != "replace" and not os.path.exists(file_path):
            return {"status": "error", "message": f"File '{file_path}' does not exist."}

        # Execute based on mode
        if mode == "append":
            return _append_to_file(file_path, content)
        elif mode == "replace":
            return _replace_file(file_path, content)
        elif mode == "insert":
            return _insert_at_line(file_path, content, line_number)

    except Exception as e:
        return {"status": "error", "message": f"Error editing file: {str(e)}"}


def _append_to_file(file_path: str, content: str) -> Dict[str, Any]:
    """Append content to end of file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{content}")

    return {
        "status": "success",
        "message": f"Appended to file: '{file_path}'",
        "mode": "append"
    }


def _replace_file(file_path: str, content: str) -> Dict[str, Any]:
    """Replace entire file content."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return {
        "status": "success",
        "message": f"Replaced content in file: '{file_path}'",
        "mode": "replace"
    }


def _insert_at_line(file_path: str, content: str, line_number: int) -> Dict[str, Any]:
    """Insert content at specific line."""
    # Read existing content
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Validate line number
    if line_number < 1:
        return {"status": "error", "message": "line_number must be >= 1"}

    if line_number > len(lines) + 1:
        return {
            "status": "error",
            "message": f"line_number {line_number} is beyond file length ({len(lines)} lines)"
        }

    # Insert content (convert to 0-indexed)
    insert_index = line_number - 1
    lines.insert(insert_index, content + '\n')

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return {
        "status": "success",
        "message": f"Inserted content at line {line_number} in file: '{file_path}'",
        "mode": "insert",
        "line_number": line_number
    }
