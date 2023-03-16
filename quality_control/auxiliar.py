#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def json_file_to_dict(file_path: str) -> dict:
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)

def dict_to_json_file(dict: dict, file_path: str):
    file = open(file_path, "w")
    file.write(json.dumps(dict, sort_keys=True, indent=4))
    file.close()

def get_alpha2_country_codes(filename: str) -> set:
    country_codes = set()
    countries_list = json_file_to_dict(filename)
    for country in countries_list:
        country_codes.add(country["alpha-2"])
    return country_codes