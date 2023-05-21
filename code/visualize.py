#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from shapely import Polygon, MultiPolygon
# internal modules imports
from utils.constants import (
    GROUND_TRUTH_VALIDATIONS_PATH
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file,
    alpha2_code_to_alpha3
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
    # Add origin
    results_df = pd.concat([
        pd.DataFrame([[
            "origin",
            hunter_result["origin"]["latitude"],
            hunter_result["origin"]["longitude"]
        ]], columns=results_df.columns),
        results_df], ignore_index=True)
    # Add last hop
    results_df = pd.concat([
        pd.DataFrame([[
            "last_hop",
            hunter_result["last_hop"]["geolocation"]["latitude"],
            hunter_result["last_hop"]["geolocation"]["longitude"]
        ]], columns=results_df.columns),
        results_df], ignore_index=True)
    # Add pings valid
    for ping_disc in hunter_result["ping_discs"]:
        results_df = pd.concat([
            pd.DataFrame([[
                "ping_disc",
                ping_disc["latitude"],
                ping_disc["longitude"]
            ]], columns=results_df.columns),
            results_df], ignore_index=True)
    # Add airports located
    for airport in hunter_result["hunt_results"]["airports_located"]:
        results_df = pd.concat([
            pd.DataFrame([[
                "ping_disc",
                airport["latitude"],
                airport["longitude"]
            ]], columns=results_df.columns),
            results_df], ignore_index=True)

    # Plot points
    plot = px.scatter_geo(results_df,
                          lat="latitude",
                          lon="longitude",
                          hover_name="type",
                          color="type")
    plot.show()
    #fig = go.Figure(data=go.Scattergeo(
    #    lon=results_df["longitude"],
    #    lat=results_df["latitude"],
    #    mode="markers",
    #    marker_color=results_df["type"]
    #))
    #fig.update_layout(
    #    title='Hunter Result'
    #)
    #fig.show()


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
