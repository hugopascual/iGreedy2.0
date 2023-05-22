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
    convert_km_radius_to_degrees,
    calculate_intersection
)


def plot():
    latitude = 40.4655
    longitude = -3.7
    circles = list([
        Point(longitude, latitude).buffer(
            convert_km_radius_to_degrees(km_radius=50)
        ),
        Point(longitude + 0.5, latitude + 0.5).buffer(
            convert_km_radius_to_degrees(km_radius=50)
        ),
        Point(longitude, latitude + 0.5).buffer(
            convert_km_radius_to_degrees(km_radius=50)
        ),
    ])

    fig = go.Figure()
    # Plot intersection
    intersection = calculate_intersection(circles)
    intersection_ext_coords_x, \
        intersection_ext_coords_y = intersection.exterior.coords.xy
    fig.add_trace(go.Scattergeo(
        lat=intersection_ext_coords_y.tolist(),
        lon=intersection_ext_coords_x.tolist(),
        mode="markers+lines",
        marker={"color": "goldenrod"}
    ))

    # Plot circles
    for circle in circles:
        circle_ext_coords_x, circle_ext_coords_y = circle.exterior.coords.xy

        fig.add_trace(go.Scattergeo(
            lat=circle_ext_coords_y.tolist(),
            lon=circle_ext_coords_x.tolist(),
            mode="markers+lines",
            marker={"color": "red"}
        ))
    # Figure customization
    fig.update_geos(
        projection_type="natural earth"
    )
    fig.update_layout(
        title='Test Mesh'
    )
    fig.show()


def connect_to_vpn_server(vpn_server: str) -> dict:
    if vpn_server == "Host":
        return
    else:
        #connection_result = subprocess.run([
        #    "protonvpn-cli", "connect", "--cc",
        #    vpn_server,
        #    "--protocol", "tcp"], stdout=subprocess.PIPE)
        connection_status = subprocess.run([
            "protonvpn-cli", "status"], stdout=subprocess.PIPE)
        status_params_raw = (connection_status.stdout.split("\\n")[3:])[:-6]
        status_params = []
        for param_raw in status_params_raw:
            status_params.append((param_raw.split("\\t")[-1])[1:])

        return {
            "ip": status_params[0],
            "server_name": status_params[1],
            "country": status_params[2],
            "protocol": status_params[3],
            "server_load": status_params[4]
        }

