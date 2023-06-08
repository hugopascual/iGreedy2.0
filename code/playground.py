#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
import subprocess
import re
import geocoder
import pandas as pd
import requests
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
    KEY_FILEPATH
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
    calculate_hunter_pings_intersection_area
)


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


traceroute_data = {
    "definitions": [
        {
            "target": "104.16.123.96",
            "description": "HTTP test to 104.16.123.96",
            "type": "http",
            "is_oneoff": True,
            "af": 4,
        }
    ],
    "probes": [
        {
            "requested": 1,
            "type": "country",
            "value": "NL"
        }
    ]
}
measurement_id = 55155484
url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + "/?key={}".format(get_ripe_key())

#make_ripe_measurement(data=traceroute_data)
#get_measurement_results()
