#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import httpx
import os
from urllib.parse import urljoin
from typing import Any, Dict

import authent as authent
import config_manager
from utils import ensure_directory, ssl_verify, str2bool

routines = {
    "index_time_properties": "make_index_time_properties:makeIndexTimeProperties",
    "on_prem": "make_on_prem:makeOnPrem",
}

URL_MAKEAPP = "/services/data/appmaker/makeapp"
URL_DOWNLOADAPP = "/services/data/appmaker/downloadapp"

def download_app(splunk_url, headers, verify, app, output_dir, extension) -> None:
    """
    Downloads an application from a Splunk server and saves it to the specified output directory.

    Args:
        splunk_url (str): The base URL of the Splunk server.
        headers (dict): The headers to include in the request.
        verify (bool): A boolean indicating whether SSL certificate verification is enabled.
        app (dict): A dictionary containing the application's namespace and filename.
        output_dir (str): The directory where the downloaded file will be saved.
        ext (str, optional): The extension to use for the saved file. Defaults to "tgz".

    Returns:
        None

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.

    Example:
        download_app(
            splunk_url="https://splunk.example.com",
            headers={"Authorization": "Bearer token"},
            app={"namespace": "search", "filename": "app.tgz"},
            output_dir="/path/to/output"
        )
    """

    # Ensure output directory exists
    output_path = ensure_directory(output_dir)
    if not output_path:
        print("[-] Failed to create or access output directory. Exiting.")
        return

    url = urljoin(splunk_url, URL_DOWNLOADAPP)
    params = {
        "namespace": app["namespace"],
        "filename": app["filename"]
    }  
    with httpx.Client(verify=verify) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()

        if "Content-Disposition" in response.headers:
            content_disposition = response.headers["Content-Disposition"]
            filename = content_disposition.split("filename=")[1]
        else:
            filename = URL_DOWNLOADAPP.split("/")[-1]

        name, old_extension = os.path.splitext(filename)
        new_filename = name + '.' + extension

        with open(os.path.join(output_path, new_filename), mode="wb") as file:
            file.write(response.content)

        print(f"[+] Downloaded file {new_filename} in {output_dir}")

def make_app(splunk_url, headers, verify, data) -> Dict[str, Any]:
    """
    Create a new app in Splunk. Based on Distributed configuration management in General settings.
    
    Args:
        splunk_url (str): The base URL of the Splunk instance.
        headers (dict): The headers to include in the HTTP request.
        verify (bool): A boolean indicating whether SSL certificate verification is enabled.
        data (dict): The data to send in the HTTP request body.
        
    Returns:
        dict: The JSON response from the Splunk server.
        
    Raises:
        SystemExit: If the HTTP request fails with a status code other than 200.
    """
    url = urljoin(splunk_url, URL_MAKEAPP)
    try:
        with httpx.Client(verify=verify) as client:
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"[-] Error making app: {e.response.text}")
        exit(2)
    except httpx.RequestError as e:
        print(f"[-] Error making app: {str(e)}")
        exit(3)
    return response.json()

def make_config() -> Dict[str, Any]:
    """
    Create a configuration dictionary from the command line arguments and configuration files.

    Returns:
        Dictionary containing the configuration
    """
    config = config_manager.ConfigurationManager()
    config.add_argument("--url_mgmt", "-u", type=str, help="Splunk host URL", required=False)
    config.add_argument("--username", "-U", type=str, help="Splunk username", required=False)
    config.add_argument("--token", "-t", type=str, help="Splunk authentication token", required=False)
    config.add_argument("--routine", "-r", type=str, help="Routine to execute", choices=["index_time_properties","on_prem"], required=False)
    config.add_argument("--indexes", "-i", type=str, help="Indexes to include", default=False, required=False, action=argparse.BooleanOptionalAction)
    config.add_argument("--properties", "-p", type=str, help="Properties to include", default=False, required=False, action=argparse.BooleanOptionalAction)
    config.add_argument("--output", "-o", type=str, help="Output directory", default="./", required=False)
    config.add_argument("--extension", "-e", type=str, help="Extension for the downloaded file", choices=["spl", "tar.gz", "tgz"], required=False)
    config.add_argument("--verify", "-v", type=str, help="Verify SSL certificate", default=False, required=False, action=argparse.BooleanOptionalAction)
    args = config.parser.parse_args()

    config.load_config_file(args.config)
    config.set_config(section="ssl",key="verify", env_key="SSL_DCD_VERIFY", default=str(False))
    config.set_config(section="app",key="indexes", env_key="SPLUNK_DCD_INDEXES", default=str(False))
    config.set_config(section="app",key="properties", env_key="SPLUNK_DCD_PROPERTIES", default=str(False))
    config.set_config_group(section="splunk", keys=["url_mgmt", "username", "token"], env_prefix="SPLUNK_DCD")
    config.set_config_group(section="app", keys=["extension", "routine", "output"], env_prefix="APP_DCD",)
    
    return config.config_data

def set_data(config, routines) -> Dict[str, str]:
    """
    Generates a dictionary of data based on the provided configuration.

    Args:
        config (dict): A dictionary containing configuration settings. Expected keys are:
            - "app.indexes": (optional) A value indicating whether indexes should be included.
            - "app.properties": (optional) A value indicating whether properties should be included.
            - "app.routine": A key indicating the routine to be used.
        routines (dict): A dictionary of routines and their corresponding Splunk endpoint names.

    Returns:
        Dict[str, str]: A dictionary containing the processed data. Keys include:
            - "routine": The routine value from the provided configuration.
            - "spec": A JSON string specifying whether indexes and properties are included, 
                      if the routine is "index_time_properties".
    """
    data: Dict[str, str] = {}
    indexes = str(config.get("app.indexes")).lower()
    properties = str(config.get("app.properties")).lower()
    data['routine'] = routines[config.get("app.routine")]
    if config.get("app.routine") == "index_time_properties":
        data["spec"] = f'{{"include_indexes":{indexes}, "include_properties":{properties}}}'
    return data

def main():
    """
    Main function for the Splunk distributed configuration management downloader.
    """

    config = make_config()
    url = config.get("splunk.url_mgmt")
    verify = str2bool(ssl_verify(config.get("ssl.verify")))

    print(f"[+] Splunk URL: {config.get("splunk.url_mgmt")}")

    headers = authent.get_token(url, config.get("splunk.username"), config.get("splunk.token"))
    if not headers:
        print("[-] Authentication failed. Exiting.")
        exit(1)

    data = set_data(config, routines)
    app = make_app(url, headers, verify, data)
    download_app(url, headers, verify, app, config.get("app.output"), config.get("app.extension"))

if __name__ == "__main__":
    main()