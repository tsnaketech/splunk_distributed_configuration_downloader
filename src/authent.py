#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getpass
import httpx
from typing import Dict, Optional

URI_LOGIN = "/services/auth/login"

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
    auth_url = splunk_url + URI_LOGIN
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
        raise Exception(f"[-] Authentication error - HTTP {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        raise Exception(f"[-] Authentication error - Connection failed: {str(e)}")
    except KeyError as e:
        raise Exception(f"[-] Authentication error - Unexpected response format: {str(e)}")