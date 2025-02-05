#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib3
from pathlib import Path
from typing import Optional, Union

def ensure_directory(directory: Union[str, Path]) -> Optional[str]:
    """
    Ensures that a directory exists, creating it if necessary.

    Args:
        directory: Directory path as string or Path object

    Returns:
        str: Path of the created/existing directory if successful
        None: If creation fails

    Raises:
        PermissionError: When user doesn't have permission to create directory
        OSError: For other system-level errors
    """
    try:
        # Convert to Path object for better path handling
        dir_path = Path(directory)

        # Create parent directories if they don't exist
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[+] Created directory: {dir_path}")

        # Ensure the path is actually a directory
        if not dir_path.is_dir():
            print(f"[-] Error: Path exists but is not a directory: {dir_path}")
            return None

        # Convert to absolute path
        return str(dir_path.absolute())

    except PermissionError:
        print(f"[-] Error: Permission denied when creating directory: {directory}")
        return None
    except OSError as e:
        print(f"[-] Error creating directory {directory}: {str(e)}")
        return None

def ssl_verify(verity) -> bool:
    """
    Check if SSL certificate verification is enabled.

    Args:
        verify (bool): A boolean indicating whether SSL certificate verification is enabled.

    Returns:
        bool: True if SSL certificate verification is enabled, False otherwise.
    """
    # Check if the configuration has a value for "splunk.verify"
    if not verity:
        # Disable security warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return verify

def str2bool(v):
    """
    Convert a string representation of truth to a boolean.

    Args:
        v (str): The string to convert. Expected values are "yes", "true", "t", "1" (case insensitive).

    Returns:
        bool: True if the string represents a truth value, False otherwise.
    """
    return str(v).lower() in ("yes", "true", "t", "1")
