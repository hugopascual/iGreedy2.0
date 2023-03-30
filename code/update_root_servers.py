#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
# internal modules imports
from utils.constants import (
    ROOT_SERVERS_URL,
    ROOT_SERVERS_PATH,
    ROOT_SERVERS_NAMES
)
from utils.functions import (
    dict_to_json_file
)

def update_root_servers_json():
    for root_name in ROOT_SERVERS_NAMES:
        request = requests.get(url=ROOT_SERVERS_URL+root_name+"/json").json()
        root_servers_filename = "root_servers_{}.json".format(root_name)
        dict_to_json_file(dict=request, 
                          file_path=ROOT_SERVERS_PATH+root_servers_filename)