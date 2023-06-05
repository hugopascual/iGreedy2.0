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
