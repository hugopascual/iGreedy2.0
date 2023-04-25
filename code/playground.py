#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import shapely
import ast
import random
import requests
import geocoder
from shapely.geometry import MultiPolygon, Polygon, box, MultiPoint, Point, shape
from shapely import wkt
from shapely import from_geojson, GeometryCollection
from utils.common_functions import (
    json_file_to_list,
    dict_to_json_file,
    json_file_to_dict,
    is_probe_inside_section,
    get_polygon_from_section
)
from visualize import (
    plot_polygon,
    plot_multipolygon
)

metrics_csv_file = "104.16.123.96_Europe-countries_20230413_alpha_light-factor_0.18.csv"
array_split = metrics_csv_file.split("_")
print(array_split)
campaign_name = array_split[1:3] + array_split[4:]
print(campaign_name)

