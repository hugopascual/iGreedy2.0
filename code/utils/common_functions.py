#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
import json
import csv
import math
import os
# internal modules imports
from utils.constants import (
    ROOT_SERVERS_NAMES,
    ROOT_SERVERS_URL,
    ROOT_SERVERS_PATH,
    EARTH_RADIUS_KM,
    ALL_COUNTRIES_FILE_PATH
)


def create_directory_structure(path: str) -> None:
    # Remove files from path, only directories
    if path[-1] != "/":
        path = "/".join(path.split("/")[:-1])

    if not os.path.exists(path):
        os.makedirs(path)


def update_root_servers_json():
    for root_name in ROOT_SERVERS_NAMES:
        request = requests.get(url=ROOT_SERVERS_URL+root_name+"/json").json()
        root_servers_filename = "root_servers_{}.json".format(root_name)
        dict_to_json_file(dict=request, 
                          file_path=ROOT_SERVERS_PATH+root_servers_filename)


def json_file_to_dict(file_path: str) -> dict:
    create_directory_structure(file_path)
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)


def json_file_to_list(file_path: str) -> list:
    create_directory_structure(file_path)
    with open(file_path) as file:
        raw_json = file.read()

    return json.loads(raw_json)


def dict_to_json_file(dict: dict, file_path: str):
    create_directory_structure(file_path)
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()


def list_to_json_file(dict: list, file_path: str):
    create_directory_structure(file_path)
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()


def list_of_dicts_to_csv(list: list, file_path: str):
    create_directory_structure(file_path)
    keys = list[0].keys()

    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list)


def distance(a: dict, b: dict) -> float:
    lat1 = a["latitude"]
    lat2 = b["latitude"]
    lon1 = a["longitude"]
    lon2 = b["longitude"]

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi / 180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians

    # theta = longitude
    theta1 = lon1 * degrees_to_radians
    theta2 = lon2 * degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    if abs(cos - 1.0) < 0.000000000000001:
        arc = 0.0
    else:
        arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * EARTH_RADIUS_KM


def alpha2_code_to_alpha3(alpha2: str) -> str:
    all_countries_list = json_file_to_dict(ALL_COUNTRIES_FILE_PATH)
    for country in all_countries_list:
        if alpha2 == country["alpha-2"]:
            return country["alpha-3"]


def get_list_files_in_path(path: str) -> list:
    files_in_path = \
        [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files_in_path
