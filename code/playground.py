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
)

campaign_path = "{}{}".format(
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    "20230522_validation_anycast_cloudfare")
results_filenames = get_list_files_in_path(campaign_path)

airports_df = pd.read_csv("datasets/airports.csv", sep="\t")
airports_df.drop(["pop",
                  "heuristic",
                  "1", "2", "3"], axis=1, inplace=True)

for result_filename in results_filenames:
    result_dict = json_file_to_dict("{}/{}".format(
        campaign_path, result_filename)
    )
    gt_iata_code = result_dict["gt_code"]
    print(gt_iata_code, result_filename)
    mask = airports_df["#IATA"].values == gt_iata_code
    gt_airport = airports_df[mask].to_dict("records")[0]

    result_dict["gt_info"] = result_dict.pop("gt_code")
    result_dict["gt_info"] = gt_airport

    dict_to_json_file(result_dict, "{}/{}".format(
        campaign_path, result_filename))

