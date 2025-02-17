#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import getpass
import json
import os
from pathlib import Path
from typing import Optional, Union

from splunklib.client import Entity, Collection, KVStoreCollection, KVStoreCollections, Service

PATH_COLLECTIONS = '/services/configs/conf-collections'
PATH_LOOKUPS = '/services/data/transforms/lookups'
PATH_LOOKUPS_FILE = 'data/lookup-table-files'

PATH_MAKEAPP = "/services/data/appmaker/makeapp"
PATH_DOWNLOADAPP = "/services/data/appmaker/downloadapp"

class Splunk(Service):
    def __init__(self, **kwargs):
        Service.__init__(self, **kwargs)

    @property
    def collections(self):
        return Collections(self)

    @property
    def lookups(self):
        return Lookups(self)

    @property
    def lookups_file(self):
        return LookupsFile(self)

    @property
    def distributed_configuration_management(self):
        return DistributedConfigurationManagement(self)

class KVCollection(KVStoreCollection):
    """This class represents a search collection."""
    def _make_list(self, field):
        resutls = {}
        for k, v in self._state.content.items():
            if k.startswith(field):
                try:
                    resutls[k.split(".")[1]] = int(v) if v.isdigit() else v.strip()
                except AttributeError:
                    resutls[k.split(".")[1]] = v.strip()
        return resutls or None

    @property
    def accelerated_fields(self) -> list:
        return self._make_list('accelerated_fields')

    @property
    def fields(self) -> list:
        return self._make_list('field')

class Collections(KVStoreCollections):
    """This class represents a collection of objects. Retrieve this
    collection using :meth:`Splunk.collections`."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_COLLECTIONS, item=KVCollection)

class Lookup(Entity):
    """This class represents a search lookup."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

class Lookups(Collection):
    """This class represents a collection of lookups. Retrieve this
    collection using :meth:`Splunk.lookups`."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_LOOKUPS, item=Lookup)

class LookupFile(Entity):
    """This class represents a search lookup_file."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)
        self.data, self.reader, self.rows = self._get_data()

    def _get_data(self):
        from io import StringIO
        response = self.service.jobs.oneshot(f'| inputlookup {self._state.get('title', '')}', output_mode='csv').read()
        data = response.decode('utf-8').lstrip('\n')
        reader = csv.DictReader(StringIO(data))
        rows = list(reader)
        return data, reader, rows

    def download(self, output_file):
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.reader.fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)
        return True

class LookupsFile(Collection):
    """This class represents a collection of macros. Retrieve this
    collection using :meth:`Splunk.lookups_file`."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_LOOKUPS_FILE, item=LookupFile)

class DistributedConfigurationManagement():
    """This class represents a search lookup."""
    def __init__(self, service):
        self.service = service

    def make_app(self, params) -> dict:
        """
        Creates an application with the given parameters.

        Args:
            params (dict): A dictionary of parameters required to create the application.
                - routine (str): The routine to use to create the application.
                - spec (str): The spec to use to create the application.
                    - include_indexes (bool): A value indicating whether indexes should be included.
                    - include_properties (bool): A value indicating whether properties should be included.

        Returns:
            dict: A dictionary containing the response from the service after creating the application.
                - filename (str): The name of the application file.
                - namespace (str): The namespace of the application.

        Raises:
            None

        Example:
            make_app({"routine": "make_index_time_properties:makeIndexTimeProperties", "spec": '{"include_indexes":true, "include_properties":false}'})
        """

        response = self.service.post(PATH_MAKEAPP, body=params)
        return json.load(response.body)

    def download_app(self, output_dir, extension, params=None) -> None:
        """
        Downloads an application from the Splunk service and saves it to the specified output directory.

        Args:
            output_dir (str): The directory where the downloaded file will be saved.
            extension (str): The file extension to be used for the downloaded file.
            params (dict, optional): Additional parameters for the download request. If 'routine' is present in params,
                         it will be used to generate the request body using the make_app method. Otherwise,
                         params will be used directly as the request body.

        Returns:
            None

        Raises:
            None

        Side Effects:
            Creates the output directory if it does not exist.
            Writes the downloaded file to the specified output directory.

        Example:
            download_app("/path/to/output", "tar.gz", {"filename": "1739234964_Splunk_TA_ForIndexers-1.0.0-0.spl", "namespace": "SA-Utils"})
            download_app("/path/to/output", "spl", {"routine": "make_index_time_properties", "spec": '{"include_indexes":true, "include_properties":false}'})
        """

        # Ensure output directory exists
        output_path = ensure_directory(output_dir)
        if not output_path:
            print("[-] Failed to create or access output directory. Exiting.")
            return

        if params.get("routine"):
            body = self.make_app(params)
        else:
            body = params

        print(f"[+] Downloading app with params: {body}")

        response = self.service.get(PATH_DOWNLOADAPP, **body)
        headers = dict(response.headers)

        if "Content-Disposition" in headers:
            content_disposition = headers["Content-Disposition"]
            filename = content_disposition.split("filename=")[1]
        else:
            filename = PATH_DOWNLOADAPP.split("/")[-1] + "." + extension

        filename = "Splunk_" + filename

        name, old_extension = os.path.splitext(filename)
        new_filename = name + '.' + extension

        with open(os.path.join(output_path, new_filename), mode="wb") as file:
            file.write(response.body.readall())

        print(f"[+] Downloaded file {new_filename} in {output_dir}")

def login(**kwargs):
    """
    Authenticate to Splunk and return a service object.

    Args:
        scheme: Splunk management scheme
        host: Splunk management host
        port: Splunk management port
        username: Splunk username
        token: Splunk authentication token
        verify: Verify SSL certificates
    """
    if not kwargs["username"] and kwargs["token"]:
        service = Splunk(**kwargs)
    else:
        kwargs["passowrd"] = getpass.getpass(prompt='[?] Splunk Password: ')
        service = Splunk(**kwargs)
    service.login()
    return service

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

    # Convert to Path object for better path handling
    dir_path = Path(directory)

    # Create parent directories if they don't exist
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[+] Created directory: {dir_path}")

    # Ensure the path is actually a directory
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path exists but is not a directory: {dir_path}")

    # Convert to absolute path
    return str(dir_path.absolute())