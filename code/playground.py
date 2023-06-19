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

df = pd.read_csv(GT_VALIDATIONS_STATISTICS +
                 "statistics_North-Central_validation_20230410.csv",
                 sep=",")

df_optimal = df[
    (df["probe_selection"] == "area") &
    (df["probe_set_number"] == 500) &
    (df["distance_function"] == "verloc_aprox") &
    (df["threshold"] == 1) &
    (df["alpha"] == 1)
]

df_optimal = df_optimal[["target", "Accuracy", "Precision", "Recall", "F1", "gt_instances_in_region"]]
df_optimal.to_csv(GT_VALIDATIONS_STATISTICS + "optimal_params_results.csv",
          sep=",",
          index=False)

df_second_optimal = df[
    (df["probe_selection"] == "area") &
    (df["probe_set_number"] == 1000) &
    (df["distance_function"] == "constant_1.52") &
    (df["threshold"] == 1) &
    (df["alpha"] == 1)
]
df_second_optimal = df_second_optimal[["target", "Accuracy", "Precision", "Recall", "F1", "gt_instances_in_region"]]
df_second_optimal.to_csv(GT_VALIDATIONS_STATISTICS + "optimal_second_params_results.csv",
          sep=",",
          index=False)
