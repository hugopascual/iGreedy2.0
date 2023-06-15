#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
import subprocess
import re
import geocoder
import pandas as pd
import requests
import ipinfo
import datetime
from subprocess import run

import shapely
from shapely import (
    Point,
    Polygon
)
from shapely.ops import unary_union
from rtree import index
import plotly.graph_objects as go
from utils.constants import (
    FIBER_RI,
    SPEED_OF_LIGHT,
    EARTH_RADIUS_KM,
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    VERLOC_GAP,
    VERLOC_APROX_PATH,
    RIPE_ATLAS_MEASUREMENTS_BASE_URL,
    KEY_FILEPATH,
    AREA_OF_INTEREST_FILEPATH,
    GT_VALIDATIONS_STATISTICS,
    CLOUDFARE_IPS,
    ROOT_SERVERS
)
from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance,
    json_file_to_dict,
    dict_to_json_file,
    convert_km_radius_to_degrees,
    get_list_files_in_path,
    get_nearest_airport_to_point,
    calculate_hunter_pings_intersection_area,
    get_polygon_from_section,
    get_list_folders_in_path
)
from groundtruth import get_gt_instances_locations


def get_ripe_key() -> str:
    return json_file_to_dict(KEY_FILEPATH)["key"]


def make_ripe_measurement(data: dict):
    # Start the measurement and get measurement id
    response = {}
    try:
        response = requests.post(url, json=data).json()
        measurement_id = response["measurements"][0]
        print(measurement_id)
    except Exception as e:
        print(e.__str__())
        print(response)


def get_measurement_results():
    results_measurement_url = \
        RIPE_ATLAS_MEASUREMENTS_BASE_URL + "{}/results".format(
            measurement_id
        )

    print(results_measurement_url)
    response = requests.get(results_measurement_url).json()
    dict_to_json_file(response, "http_petition.json")


url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + "/?key={}".format(get_ripe_key())
traceroute_data = {
    "definitions": [
        {
            "target": "104.16.123.96",
            "description": "HTTP test to 104.16.123.96",
            "type": "http",
            "is_oneoff": True,
            "header_bytes": 2048,
            "af": 4,
        }
    ],
    "probes": [
        {
            "requested": 5,
            "type": "country",
            "value": "NL"
        }
    ]
}
#make_ripe_measurement(data=traceroute_data)

#measurement_id = 55212992
#get_measurement_results()


igreedy_statistics_df = pd.read_csv(
    GT_VALIDATIONS_STATISTICS +
    "statistics_North-Central_validation_20230410.csv")

# dataframe con los optimos de cada escenario
optimal_params_df = pd.DataFrame()
target_list = CLOUDFARE_IPS + list(ROOT_SERVERS.keys())

for target in target_list:
    target_df = igreedy_statistics_df[
        igreedy_statistics_df["target"] == target]
    target_df = target_df[target_df["Precision"] == target_df["Precision"].max()]
    target_df = target_df[target_df["Recall"] == target_df["Recall"].max()]
    target_df = target_df[target_df["F1"] == target_df["F1"].max()]
    target_df = target_df[target_df["Accuracy"] == target_df["Accuracy"].max()]
    target_optimal = target_df
    target_optimal.sort_values(by=["threshold", "alpha"], inplace=True)

    optimal_params_df = pd.concat(
        [target_optimal, optimal_params_df], ignore_index=True)

optimal_params_df.sort_values(by=["target", "threshold", "alpha"])
optimal_params_df.to_csv(
    GT_VALIDATIONS_STATISTICS + "optimal_params_by_target.csv",
    sep=","
)
