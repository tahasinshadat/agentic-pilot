"""
Path validation utility for security.
Prevents path traversal attacks and restricts file operations to safe directories.
"""

import os
from pathlib import Path
from typing import Optional


def validate_file_path(file_path: str, allow_absolute: bool = True) -> tuple[bool, Optional[str]]:
    """
    Validate that a file path is safe to use.

    Args:
        file_path: Path to validate
        allow_absolute: Whether to allow absolute paths

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Convert to Path object
        path = Path(file_path)

        # Check for path traversal attempts
        path_str = str(path).replace('\\', '/')
        if '..' in path_str or path_str.startswith('/'):
            # Check if it's trying to escape current directory
            try:
                resolved = path.resolve()
                cwd = Path.cwd().resolve()
                
                # If path goes outside cwd, only allow if it's explicitly an absolute path
                if not allow_absolute and not str(resolved).startswith(str(cwd)):
                    return False, f"Path traversal detected: {file_path} escapes current directory"
            except (ValueError, OSError) as e:
                return False, f"Invalid path: {str(e)}"

        # Check for dangerous path components
        dangerous_components = ['..', '~', '$']
        for component in path.parts:
            if any(danger in component for danger in dangerous_components):
                if component != '..':  # .. was already handled above
                    return False, f"Dangerous path component detected: {component}"

        # Path is safe
        return True, None

    except Exception as e:
        return False, f"Path validation error: {str(e)}"


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitize a file path by removing dangerous components.

    Args:
        file_path: Path to sanitize

    Returns:
        str: Sanitized path
    """
    # Remove leading slashes for relative paths
    path = file_path.lstrip('/')
    
    # Remove path traversal attempts
    parts = []
    for part in Path(path).parts:
        if part != '..' and part != '.':
            parts.append(part)
    
    return str(Path(*parts)) if parts else '.'
