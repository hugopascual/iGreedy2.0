#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv

def json_file_to_dict(file_path: str) -> dict:
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)

def dict_to_json_file(dict: dict, file_path: str):
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()

def list_to_json_file(dict: list, file_path: str):
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()

def get_alpha2_country_codes_from_file(filename: str) -> set:
    country_codes = set()
    countries_list = json_file_to_dict(filename)
    for country in countries_list:
        country_codes.add(country["alpha-2"])
    return country_codes

def list_of_dicts_to_csv(list: list, filepath: str):
    
    keys = list[0].keys()

    with open(filepath, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list)