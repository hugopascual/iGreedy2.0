#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

import shapely
from shapely import Point, Polygon, MultiPolygon
# internal modules imports
from utils.constants import (
    GROUND_TRUTH_VALIDATIONS_PATH
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file,
    alpha2_code_to_alpha3,
    convert_km_radius_to_degrees
)


def plot_file(filepath: str) -> None:
    try:
        data_keys = json_file_to_dict(filepath).keys()
    except Exception as e:
        print("Exception provocated because bad file")
        print(e)
        return

    if "measurement_id" in data_keys:
        plot_measurement(filepath)
    elif "num_anycast_instances" in data_keys:
        plot_result(filepath)
    elif "statistics" in data_keys:
        plot_groundtruth_validation(filepath)
    elif "last_hop" in data_keys:
        plot_hunter_result(filepath)
    else:
        print("File is neither a measurement, a result or a gt validation "
              "recognized")


def plot_measurement(measurement_path: str) -> None:
    # TODO add radius of rtt to the plot
    measurement_results_df = pd.DataFrame(
        json_file_to_dict(measurement_path)["measurement_results"])

    plot = px.scatter_geo(measurement_results_df,
                          lat="latitude",
                          lon="longitude",
                          hover_name="hostname",
                          hover_data=['rtt_ms'])
    plot.show()


def plot_result(result_path: str) -> None:
    results_instances = json_file_to_dict(result_path)["anycast_instances"]
    measurement_probes_df = get_measurement_probes_from_results_file(
        result_path)

    markers = []
    for instance in results_instances:
        markers.append(instance["marker"])
    result_instances_df = pd.DataFrame(markers)
    result_instances_df["type"] = "result_instance"

    id_probes_selected = []
    for instance in results_instances:
        id_probes_selected.append(instance["circle"]["id"])
    measurement_probes_df["type"] = measurement_probes_df["id"].apply(
        lambda x: "probe_selected" if x in id_probes_selected else "probe")

    plot_df = pd.concat([measurement_probes_df, result_instances_df])
    plot = px.scatter_geo(plot_df,
                          lat="latitude",
                          lon="longitude",
                          hover_name="city",
                          hover_data=['rtt_ms'],
                          color="type")
    plot.show()


def plot_groundtruth_validation(gt_validation_path: str) -> None:
    gt_validation_dict = json_file_to_dict(gt_validation_path)
    measurement_probes_df = get_measurement_probes_from_results_file(
        gt_validation_dict["results_filepath"])
    instances_validated_df = pd.DataFrame(gt_validation_dict["instances"])

    # Remove unshared fields
    measurement_probes_df.drop(columns="id", inplace=True)
    instances_validated_df.drop(columns="country_code", inplace=True)

    plot_df = pd.concat([measurement_probes_df, instances_validated_df])
    plot = px.scatter_geo(plot_df,
                          lat="latitude",
                          lon="longitude",
                          hover_name="city",
                          hover_data=['rtt_ms'],
                          color="type")
    plot.show()


def plot_hunter_result(filepath: str) -> None:
    hunter_result = json_file_to_dict(filepath)
    results_df = pd.DataFrame(columns=["type", "latitude", "longitude"])
    fig = go.Figure()
    # Add origin
    fig.add_trace(go.Scattergeo(
        lat=[hunter_result["origin"]["latitude"]],
        lon=[hunter_result["origin"]["longitude"]],
        mode="markers",
        marker={"color": "green"},
        name="origin"
    ))
    # Add last hop
    fig.add_trace(go.Scattergeo(
        lat=[hunter_result["last_hop"]["geolocation"]["latitude"]],
        lon=[hunter_result["last_hop"]["geolocation"]["longitude"]],
        mode="markers",
        marker={"color": "blue"},
        name="last_hop"
    ))
    # Add pings valid
    discs_to_intersect = []
    probes_latitudes = []
    probes_longitudes = []
    for ping_disc in hunter_result["ping_discs"]:
        probes_latitudes.append(ping_disc["latitude"])
        probes_longitudes.append(ping_disc["longitude"])
        disc = Point(
            ping_disc["longitude"],
            ping_disc["latitude"]
        ).buffer(convert_km_radius_to_degrees(ping_disc["radius"]))
        discs_to_intersect.append(disc)

    fig.add_trace(go.Scattergeo(
        lat=probes_latitudes,
        lon=probes_longitudes,
        mode="markers",
        marker={"color": "magenta"},
        name="ping_probes"
    ))

    ###
    #for disc in discs_to_intersect:
    #    disc_ext_coords_x, disc_ext_coords_y = disc.exterior.coords.xy
    #
    #    fig.add_trace(go.Scattergeo(
    #        lat=disc_ext_coords_y.tolist(),
    #        lon=disc_ext_coords_x.tolist(),
    #        mode="markers+lines",
    #        marker={"color": "red"},
    #        name="ping_discs"
    #    ))
    ###

    intersection = shapely.intersection_all(discs_to_intersect)
    intersection_ext_coords_x, \
        intersection_ext_coords_y = intersection.exterior.coords.xy
    fig.add_trace(go.Scattergeo(
        lat=intersection_ext_coords_y.tolist(),
        lon=intersection_ext_coords_x.tolist(),
        mode="markers+lines",
        marker={"color": "goldenrod"},
        name="pings_intersection"
    ))
    # Add airports located
    airports_latitudes = [
        airport["latitude"]
        for airport in hunter_result["hunt_results"]["airports_located"]
    ]
    airports_longitudes = [
        airport["longitude"]
        for airport in hunter_result["hunt_results"]["airports_located"]
    ]
    fig.add_trace(go.Scattergeo(
        lat=airports_latitudes,
        lon=airports_longitudes,
        mode="markers",
        marker={"color": "red"},
        name="airports_result"
    ))

    # Add GT location
    gt_info = hunter_result["gt_info"]
    (gt_latitude, gt_longitude) = gt_info["lat long"].split(" ")
    fig.add_trace(go.Scattergeo(
        lat=[gt_latitude],
        lon=[gt_longitude],
        mode="markers",
        marker={"color": "black"},
        name="gt"
    ))


    # Custom figure
    fig.update_geos(
        projection_type="natural earth"
    )
    fig.update_layout(
        title='Hunter Result'
    )
    fig.show()


def get_measurement_probes_from_results_file(result_path: str) -> pd.DataFrame:
    measurement_filepath = json_file_to_dict(
        result_path)["measurement_filepath"]
    measurement_probes = json_file_to_dict(
        measurement_filepath)["measurement_results"]

    measurement_probes_df = pd.DataFrame(measurement_probes)
    measurement_probes_df = measurement_probes_df[
        ["hostname", "latitude", "longitude", "rtt_ms"]]
    measurement_probes_df['id'] = measurement_probes_df.loc[:, 'hostname']
    measurement_probes_df.rename(columns={"hostname": "city"}, inplace=True)
    measurement_probes_df["type"] = "probe"

    return measurement_probes_df


def plot_polygon(polygon: Polygon):
    longitudes = []
    latitudes = []

    polygon_ext_coords_x, polygon_ext_coords_y = polygon.exterior.coords.xy
    longitudes = longitudes + polygon_ext_coords_x.tolist()
    latitudes = latitudes + polygon_ext_coords_y.tolist()

    fig = go.Figure(data=go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers'
    ))
    fig.update_geos(
        projection_type="natural earth"
    )
    fig.update_layout(
        title='Test Mesh'
    )
    fig.show()


def plot_multipolygon(multipolygon: MultiPolygon):
    longitudes = []
    latitudes = []
    for polygon in list(multipolygon.geoms):
        polygon_ext_coords_x, polygon_ext_coords_y = polygon.exterior.coords.xy
        longitudes = longitudes + polygon_ext_coords_x.tolist()
        latitudes = latitudes + polygon_ext_coords_y.tolist()

    fig = go.Figure(data=go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers'
    ))
    fig.update_geos(
        projection_type="natural earth"
    )
    fig.update_layout(
        title='Test Mesh'
    )
    fig.show()
