#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib3

def ssl_verify(verify) -> bool:
    """
    Check if SSL certificate verification is enabled.

    Args:
        verify (bool): A boolean indicating whether SSL certificate verification is enabled.

    Returns:
        bool: True if SSL certificate verification is enabled, False otherwise.
    """
    # Check if the configuration has a value for "splunk.verify"
    if not verify:
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
