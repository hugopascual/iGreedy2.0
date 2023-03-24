#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from auxiliar import (
    json_file_to_dict
)

# Constants
measurements_path = "../datasets/measurement/"
results_path = "../../results/"
root_servers_gt_path = "../datasets/root_servers/"

# Funtions
def load_data_root_servers(file_name: str) -> dict:
    root_servers_raw_data = json_file_to_dict(
        root_servers_gt_path + file_name)

    root_servers_gt = {}
    for instance in root_servers_raw_data["Sites"]:
        if instance["Country"] in root_servers_gt.keys():
            town = {
                "city_name": instance["Town"],
                "latitude": instance["Latitude"],
                "longitude": instance["Longitude"]
                }
            if town not in root_servers_gt[instance["Country"]]:
                root_servers_gt[instance["Country"]].append(town)
        else:
            root_servers_gt[instance["Country"]] = [{
                "city_name": instance["Town"],
                "latitude": instance["Latitude"],
                "longitude": instance["Longitude"]
                }]

    return root_servers_gt

def load_data_results(file_name:str) -> dict:
    results_raw_data = json_file_to_dict(
        results_path + file_name)

    results = {}
    for instance in results_raw_data["instances"]:
        marker = instance["marker"]
        if marker["code_country"] in results.keys():
            town = {
                "city_name": marker["city"],
                "latitude": marker["latitude"],
                "longitude": marker["longitude"]
                }
            if town not in results[marker["code_country"]]:
                results[marker["code_country"]].append(town)
        else:
            results[marker["code_country"]] = [{
                "city_name": marker["city"],
                "latitude": marker["latitude"],
                "longitude": marker["longitude"]
                }]

    return results