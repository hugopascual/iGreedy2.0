#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
import json
import csv
import math
import os
from shapely import Polygon, box
# internal modules imports
from utils.constants import (
    ROOT_SERVERS_NAMES,
    ROOT_SERVERS_URL,
    ROOT_SERVERS_PATH,
    EARTH_RADIUS_KM,
    ALL_COUNTRIES_FILE_PATH,
    SPEED_OF_LIGHT
)


def create_directory_structure(path: str) -> None:
    # Remove files from path, only directories
    if path[-1] != "/":
        path = "/".join(path.split("/")[:-1])
    if path == "":
        return
    if not os.path.exists(path):
        os.makedirs(path)


def update_root_servers_json():
    for root_name in ROOT_SERVERS_NAMES:
        request = requests.get(
            url=ROOT_SERVERS_URL + root_name + "/json").json()
        root_servers_filename = "root_servers_{}.json".format(root_name)
        dict_to_json_file(dict=request,
                          file_path=ROOT_SERVERS_PATH + root_servers_filename)


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


def check_discs_intersect(disc1: dict, disc2: dict) -> bool:
    centers_separation = distance(
        a={
            "latitude": disc1["latitude"],
            "longitude": disc1["longitude"]
        },
        b={
            "latitude": disc2["latitude"],
            "longitude": disc2["longitude"]
        })
    if centers_separation < (disc1["radius"] + disc2["radius"]):
        return True
    else:
        return False


def get_light_factor_from_distance(dist: float) -> float:
    return 0.0061699 * (dist**0.480214) + 0.0497791
    #return 0.152616 * math.log(0.251783 * dist + 130.598) - 0.693072

def get_time_from_distance(dist: float) -> float:
    return dist/(get_light_factor_from_distance(dist)*SPEED_OF_LIGHT)

def get_distance_from_rtt(rtt: float) -> float:
    return 0


def alpha2_code_to_alpha3(alpha2: str) -> str:
    all_countries_list = json_file_to_dict(ALL_COUNTRIES_FILE_PATH)
    for country in all_countries_list:
        if alpha2 == country["alpha-2"]:
            return country["alpha-3"]


def get_list_files_in_path(path: str) -> list:
    files_in_path = \
        [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files_in_path


def get_section_borders_of_polygon(polygon: Polygon) -> dict:
    bounds = polygon.bounds
    return {
        "longitude_min": bounds[0],
        "latitude_min": bounds[1],
        "longitude_max": bounds[2],
        "latitude_max": bounds[3]
    }


def get_polygon_from_section(section: dict) -> Polygon:
    return box(
        section["longitude_min"],
        section["latitude_min"],
        section["longitude_max"],
        section["latitude_max"]
    )


def is_point_inside_area(point: tuple, area: tuple) -> bool:
    """
    :param point: (longitude, latitude)
    :param area: (top_left_lon,top_left_lat, bottom_right_lon,bottom_right_lat)
    :return: True is point inside box, False otherwise
    """
    return (point[0] >= area[0]) & (point[0] <= area[2]) \
        & (point[1] >= area[3]) & (point[1] <= area[1])


def is_probe_inside_section(probe: dict, section: dict) -> bool:
    return is_point_inside_area(
        point=(probe["geometry"]["coordinates"][0],
               probe["geometry"]["coordinates"][1]),
        area=(section["longitude_min"],
              section["latitude_max"],
              section["longitude_max"],
              section["latitude_min"])
    )


def is_probe_usable(probe: dict, section: dict):
    if probe["status"]["name"] == "Connected":
        return is_probe_inside_section(probe=probe, section=section)
    else:
        return False
