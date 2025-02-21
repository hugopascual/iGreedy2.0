#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
import json
import csv
import math
import os
import pandas as pd
from shapely import Point, Polygon, box
from shapely import intersection_all, centroid
from shapely import to_geojson
from shapely.ops import unary_union
from rtree import index
# internal modules imports
from utils.constants import (
    ROOT_SERVERS_NAMES,
    ROOT_SERVERS_URL,
    ROOT_SERVERS_PATH,
    EARTH_RADIUS_KM,
    ALL_COUNTRIES_FILE_PATH,
    EEE_COUNTRIES_FILE_PATH,
    SPEED_OF_LIGHT,
    VERLOC_APROX_PATH,
    VERLOC_GAP
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


def dict_to_json_file(dict: dict, file_path: str, sort_keys: bool = False):
    create_directory_structure(file_path)
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4, sort_keys=sort_keys))
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
    return 0.0061699 * (dist ** 0.480214) + 0.0497791
    # return 0.152616 * math.log(0.251783 * dist + 130.598) - 0.693072


def get_time_from_distance(dist: float) -> float:
    return dist / (get_light_factor_from_distance(dist) * SPEED_OF_LIGHT)


def generate_approximation_numeric_values():
    max_distance_calculated = 5000 + VERLOC_GAP
    distances = list(range(0, max_distance_calculated, VERLOC_GAP))
    time_results = {}
    # Calculate values
    for dist in distances:
        time_travel = get_time_from_distance(dist) * 1000
        time_results[time_travel] = dist

    dict_to_json_file(time_results, VERLOC_APROX_PATH)


def get_distance_from_rtt(rtt: float) -> float:
    # We do not have the direct function, so we approximate it with the inverse
    # Set approximation values
    if rtt < 0:
        return rtt

    try:
        time_results = json_file_to_dict(VERLOC_APROX_PATH)
    except:
        generate_approximation_numeric_values()
        time_results = json_file_to_dict(VERLOC_APROX_PATH)

    trip_time_ms = rtt / 2
    # Get nearest value from calculated
    nearest_value = min(time_results,
                        key=lambda x: abs(float(x) - trip_time_ms))

    distance_result = time_results[nearest_value]
    if distance_result == 0:
        return VERLOC_GAP
    else:
        return distance_result


def alpha2_code_to_alpha3(alpha2: str) -> str:
    all_countries_list = json_file_to_dict(ALL_COUNTRIES_FILE_PATH)
    for country in all_countries_list:
        if alpha2 == country["alpha-2"]:
            return country["alpha-3"]


def get_list_files_in_path(path: str) -> list:
    files_in_path = \
        [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files_in_path


def get_list_folders_in_path(path: str) -> list:
    dirs_in_path = \
        [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return dirs_in_path


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


def convert_km_radius_to_degrees(km_radius: float) -> float:
    degree = km_radius * (360 / (2 * EARTH_RADIUS_KM * math.pi))
    return degree


def get_nearest_airport_to_point(point: Point) -> dict:
    airports_df = pd.read_csv("datasets/airports.csv", sep="\t")
    airports_df.drop(["pop",
                      "heuristic",
                      "1", "2", "3"], axis=1, inplace=True)

    airports_df["distance"] = airports_df["lat long"].apply(
        lambda airport_location: distance(
            a={
                "latitude": point.y,
                "longitude": point.x
            },
            b={
                "latitude": float(airport_location.split(" ")[0]),
                "longitude": float(airport_location.split(" ")[1])
            }
        )
    )

    return airports_df[
        airports_df["distance"] == airports_df["distance"].min()
        ].to_dict("records")[0]


def calculate_hunter_pings_intersection_area(ping_discs: list) -> dict:
    discs_to_intersect = []
    for ping_disc in ping_discs:
        if ping_disc["radius"] == -1:
            continue

        disc = Point(
            ping_disc["longitude"],
            ping_disc["latitude"]
        ).buffer(convert_km_radius_to_degrees(ping_disc["radius"]))
        discs_to_intersect.append(disc)

    intersection = intersection_all(discs_to_intersect)
    intersection_centroid = centroid(intersection)

    if intersection.is_empty:
        return {
            "intersection": None,
            "centroid": None
        }
    else:
        return {
            "intersection": to_geojson(intersection),
            "centroid": to_geojson(intersection_centroid)
        }


def get_country_name(country_code: str) -> str:
    all_countries_list = json_file_to_dict(ALL_COUNTRIES_FILE_PATH)
    for country in all_countries_list:
        if country["alpha-2"] == country_code:
            return country["name"]


def get_alpha2_country_codes(filename: str) -> set:
    return set([country["alpha-2"] for country in json_file_to_dict(filename)])


def countries_in_EEE_set() -> set:
    return get_alpha2_country_codes(EEE_COUNTRIES_FILE_PATH)



