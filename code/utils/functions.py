#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
import json

# internal modules imports
from utils.constants import (
    ROOT_SERVERS_URL,
    ROOT_SERVERS_PATH,
    ROOT_SERVERS_NAMES
)

def update_root_servers_json():
    for root_name in ROOT_SERVERS_NAMES:
        request = requests.get(url=ROOT_SERVERS_URL+root_name+"/json").json()
        root_servers_filename = "root_servers_{}.json".format(root_name)
        dict_to_json_file(dict=request, 
                          file_path=ROOT_SERVERS_PATH+root_servers_filename)

def json_file_to_dict(file_path: str) -> dict:
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)

def dict_to_json_file(dict: dict, file_path: str):
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()