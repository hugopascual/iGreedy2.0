#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH
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


campaign_path = "{}{}".format(
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    "20230522_validation_anycast_cloudfare")
results_filenames = get_list_files_in_path(campaign_path)

for result_filename in results_filenames:
    result_dict = json_file_to_dict("{}/{}".format(
        campaign_path, result_filename)
    )

    for ping_disc in result_dict["ping_discs"]:
        if ping_disc["radius"] == 0:
            ping_disc["radius"] = 10

    try:
        intersection_info = calculate_hunter_pings_intersection_area(
            result_dict["ping_discs"]
        )

        result_dict["hunt_results"]["intersection"] = \
            intersection_info["intersection"]
        result_dict["hunt_results"]["centroid"] = \
            intersection_info["centroid"]
    except Exception as e:
        print(e)

    dict_to_json_file(result_dict, "{}/{}".format(
        campaign_path, result_filename))



