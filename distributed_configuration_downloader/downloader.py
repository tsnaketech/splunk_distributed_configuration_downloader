#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from typing import Any, Dict

import config_manager, splunk
from utils import ssl_verify, str2bool

routines = {
    #"content_pack": "make_content_pack:makeContentPack",
    "index_time_properties": "make_index_time_properties:makeIndexTimeProperties",
    "on_prem": "make_on_prem:makeOnPrem",
}

def make_config() -> Dict[str, Any]:
    """
    Create a configuration dictionary from the command line arguments and configuration files.

    Returns:
        Dictionary containing the configuration
    """
    config = config_manager.ConfigurationManager()
    config.add_argument("--scheme", "-S", type=str, help="Splunk host URL scheme", required=False)
    config.add_argument("--host", "-H", type=str, help="Splunk host URL", required=False)
    config.add_argument("--port", "-P", type=int, help="Splunk management port", required=False)
    config.add_argument("--username", "-U", type=str, help="Splunk username", required=False)
    config.add_argument("--token", "-t", type=str, help="Splunk authentication token", required=False)
    config.add_argument("--routine", "-r", type=str, help="Routine to execute", choices=["index_time_properties","on_prem"], required=False)
    config.add_argument("--indexes", "-i", type=bool, help="Indexes to include", default=False, required=False, action=argparse.BooleanOptionalAction)
    config.add_argument("--properties", "-p", type=bool, help="Properties to include", default=False, required=False, action=argparse.BooleanOptionalAction)
    config.add_argument("--output", "-o", type=str, help="Output directory", default="./", required=False)
    config.add_argument("--extension", "-e", type=str, help="Extension for the downloaded file", choices=["spl", "tar.gz", "tgz"], required=False)
    config.add_argument("--verify", "-v", type=bool, help="Verify SSL certificate", default=False, required=False, action=argparse.BooleanOptionalAction)
    args = config.parser.parse_args()

    config.load_config_file(args.config)
    config.set_config(section="ssl",key="verify", env_key="SSL_DCD_VERIFY", default=str(False))
    config.set_config(section="app",key="indexes", env_key="SPLUNK_DCD_INDEXES", default=str(False))
    config.set_config(section="app",key="properties", env_key="SPLUNK_DCD_PROPERTIES", default=str(False))
    config.set_config_group(section="splunk", keys=["scheme", "host", "port", "username", "token"], env_prefix="SPLUNK_DCD")
    config.set_config_group(section="app", keys=["extension", "routine", "output"], env_prefix="APP_DCD",)

    return config.config_data

def set_data(args, routines: dict) -> Dict[str, str]:
    """
    Generates a dictionary of data based on the provided configuration.

    Args:
        args (dict): A dictionary containing configuration settings. Expected keys are:
            - "indexes": (optional) A value indicating whether indexes should be included.
            - "properties": (optional) A value indicating whether properties should be included.
            - "routine": A key indicating the routine to be used.
        routines (dict): A dictionary of routines and their corresponding Splunk endpoint names.

    Returns:
        Dict[str, str]: A dictionary containing the processed data. Keys include:
            - "routine": The routine value from the provided configuration.
            - "spec": A JSON string specifying whether indexes and properties are included,
                      if the routine is "index_time_properties".
    """
    params: Dict[str, str] = {}
    indexes = str(args.get("indexes")).lower()
    properties = str(args.get("properties")).lower()
    params['routine'] = routines[args.get("routine")]
    if args.get("routine") == "index_time_properties":
        params["spec"] = f'{{"include_indexes":{indexes}, "include_properties":{properties}}}'
    return params

def main():
    """
    Main function for the Splunk distributed configuration management downloader.
    """

    args = make_config()
    args_splunk = args.get("splunk", {})
    args_app = args.get("app", {})
    args_ssl = args.get("ssl", {})
    verify = ssl_verify(str2bool(args_ssl.get("verify")))

    print(f"[+] Splunk URL: {args_splunk.get("scheme") + "://" + args_splunk.get("host") + ":" + str(args_splunk.get("port"))}")
    service = splunk.login(verify=verify, **args_splunk)

    params = set_data(args_app, routines)
    print(f"[+] Data created: {params}")

    service.distributed_configuration_management.download_app(args_app.get("output"), args_app.get("extension"), params)

    service.logout()
    print("[+] Done.")

if __name__ == "__main__":
    main()