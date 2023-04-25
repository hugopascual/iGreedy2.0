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


def is_point_inside_area(point: tuple, area: tuple) -> bool:
    """
    :param point: (longitude, latitude)
    :param area: (top_left_lon,top_left_lat, bottom_right_lon,bottom_right_lat)
    :return: True is point inside box, False otherwise
    """
    return (point[0] >= area[0]) & (point[0] <= area[2]) \
        & (point[1] >= area[3]) & (point[1] <= area[1])


print(is_point_inside_area(
    point=(-0.0025, 51.4875),
    area=(0, 51.95,
          1, 50.95)
))