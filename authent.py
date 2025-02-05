#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getpass
import httpx
from typing import Dict, Optional

def get_token(splunk_url: str, splunk_username: Optional[str], 
              splunk_token: Optional[str], verify: bool = False) -> Optional[Dict[str, str]]:
    """
    Obtain Splunk authentication token.

    Args:
        splunk_url (str): Splunk url URL
        splunk_username (str): Splunk username
        splunk_token (str): Splunk authentication token
        verify (bool): Whether to verify SSL certificates

    Returns:
        Optional[Dict[str, str]]: Authentication headers or None if authentication fails
    """
    if not splunk_username:
        return {"Authorization": f"Bearer {splunk_token}"}

    splunk_password = getpass.getpass(prompt='[?] Splunk Password: ')
    auth_url = f"{splunk_url}/services/auth/login"
    auth_data = {
        'username': splunk_username,
        'password': splunk_password,
        'output_mode': 'json'
    }

    try:
        with httpx.Client(verify=verify) as client:
            response = client.post(auth_url, data=auth_data)
            response.raise_for_status()
            token = response.json()['sessionKey']
            return {"Authorization": f"Splunk {token}"}

    except httpx.HTTPStatusError as e:
        print(f"[-] Authentication error - HTTP {e.response.status_code}: {e.response.text}")
        return None
    except httpx.RequestError as e:
        print(f"[-] Authentication error - Connection failed: {str(e)}")
        return None
    except KeyError as e:
        print(f"[-] Authentication error - Unexpected response format: {str(e)}")
        return None