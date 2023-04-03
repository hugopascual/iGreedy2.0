#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import plotly.express as px
import pandas as pd
import json
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
                          hover_name="hostname")
    plot.show()


def get_measurement_probes_from_results_file(result_path: str) -> pd.DataFrame:
    measurement_filepath = json_file_to_dict(
        result_path)["measurement_filepath"]
    measurement_probes = json_file_to_dict(
        measurement_filepath)["measurement_results"]

    measurement_probes_df = pd.DataFrame(measurement_probes)
    measurement_probes_df = measurement_probes_df[
        ["hostname", "latitude", "longitude"]
    ]
    measurement_probes_df['id'] = measurement_probes_df.loc[:, 'hostname']
    measurement_probes_df.rename(columns={"hostname": "city"}, inplace=True)
    measurement_probes_df["type"] = "probe"

    return measurement_probes_df


def plot_result(result_path: str) -> None:
    results_instances = json_file_to_dict(result_path)["anycast_instances"]
    measurement_probes_df = get_measurement_probes_from_results_file(
        result_path)

    markers = []
    for instance in results_instances:
        markers.append(instance["marker"])
    result_instances_df = pd.DataFrame(markers)
    result_instances_df["type"] = "result_instance"

    plot_df = pd.concat([measurement_probes_df, result_instances_df])
    plot = px.scatter_geo(plot_df,
                          lat="latitude",
                          lon="longitude",
                          hover_name="city",
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
                          color="type")
    plot.show()


def plot_metrics2():
    # filepath = "ground_truth_tests/ground_truth_metrics/North-Central_campaign_20230324.csv"
    # df = pd.read_csv(filepath)
    # metric = "recall"
    # fig = px.line(df, x="alpha", y=metric, color='num_probes')
    # fig.update_layout(title = "Metrics of {} in relation to alpha and number \
    #                   of probes".format(metric))
    # fig.show()
    return


def plot_metrics():
    # area_north_central = get_alpha2_country_codes_from_file("datasets/countries_lists/North-Central_countries.json")
    # metrics_df = pd.read_csv("metrics.csv")
    # metrics_df.drop(columns="Unnamed: 0", inplace=True)
    # gt_df = get_gt_intances_locations()
    # gt_df = gt_df[gt_df["country_code"].isin(area_north_central)]
    # df = pd.concat([get_measurement_probes_locations(), metrics_df])
    # plot = px.scatter_geo(df,
    #                     lat="latitude",
    #                     lon="longitude",
    #                     hover_name="city",
    #                     color="type")
    # plot.show()
    #
    # df.sort_values("country_code", inplace=True)
    # df.to_csv("plot_metrics/test.csv")
    return
