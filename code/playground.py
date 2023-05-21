#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import subprocess
import re
import geocoder
import pandas as pd
import requests
from subprocess import run
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
    EARTH_RADIUS_KM
)
from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance,
    json_file_to_dict,
    dict_to_json_file,
    convert_km_radius_to_degrees
)


latitude = 40.4655
longitude = -3.7
circle = Point(longitude, latitude).buffer(
    convert_km_radius_to_degrees(km_radius=50)
)
circle2 = Point(longitude+1, latitude+1).buffer(
    convert_km_radius_to_degrees(km_radius=100)
)
circles = [circle, circle2]

intersections = []
idx = index.Index()

for pos, circle in enumerate(circles):
    idx.insert(pos, circle.bounds)

for circle in circles:
    merged_circles = unary_union([
        circles[pos]
        for pos in idx.intersection(circle.bounds) if circles[pos] != circle])
    intersections.append(circle.intersection(merged_circles))

intersection = unary_union(intersections)
print("Intersection")
print(intersection)
polygons_list = [intersection]

fig = go.Figure()
for polygon in polygons_list:
    longitudes = []
    latitudes = []

    polygon_ext_coords_x, polygon_ext_coords_y = polygon.exterior.coords.xy
    longitudes = longitudes + polygon_ext_coords_x.tolist()
    latitudes = latitudes + polygon_ext_coords_y.tolist()

    fig.add_trace(go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers+lines',
        marker={
            "color": "red"
        },
        showlegend=False
    ))

fig.update_geos(
    projection_type="natural earth"
)
fig.update_layout(
    title='Test Mesh'
)
fig.show()
