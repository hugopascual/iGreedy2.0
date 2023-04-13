#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# internal modules imports
from utils.constants import (
    GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file,
    get_list_files_in_path
)


def plot_campaign_statistics_comparison(validations_df: pd.DataFrame,
                                        campaign_name: str,
                                        parameter: str):
    parameter_unique_values = validations_df[parameter].unique()
    parameter_unique_values.sort()
    probes_filename_unique_values = validations_df["probes_filename"].unique()

    figure = make_subplots(rows=2,
                           cols=2,
                           subplot_titles=["Accuracy",
                                           "Precision",
                                           "Recall",
                                           "F1"])
    # Add accuracy subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=parameter_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["accuracy"],
            name=probes_filename),
                         row=1, col=1)
    # Add precision subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=parameter_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["precision"],
            name=probes_filename),
                        row=1, col=2)
    # Add recall subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=parameter_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["recall"],
            name=probes_filename),
                        row=2, col=1)
    # Add F1 subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=parameter_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["f1"],
            name=probes_filename),
                        row=2, col=2)
    figure.update_layout(title_text="{}_{}".format(campaign_name, parameter))
    figure.show()


def compare_campaign_statistics(campaign_name: str, parameter: str):
    campaign_filepath = GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH + \
                        "{}_{}/".format(campaign_name, parameter)
    try:
        validations_list = get_list_files_in_path(campaign_filepath)
    except Exception as e:
        print(e)
        return

    validations_df = pd.DataFrame(columns=[
        "target", "probes_filename",
        "alpha", "threshold", "noise",
        "accuracy", "precision", "recall", "f1"
    ])
    for validation_file in validations_list:
        data = json_file_to_dict(campaign_filepath + validation_file)
        validations_df = pd.concat(
            [pd.DataFrame([[
                data["target"],
                data["probes_filepath"].split("/")[-1][:-5],
                data["alpha"],
                data["threshold"],
                data["noise"],
                data["statistics"]["accuracy"],
                data["statistics"]["precision"],
                data["statistics"]["recall"],
                data["statistics"]["f1"]
            ]], columns=validations_df.columns),
                validations_df],
            ignore_index=True)
    validations_df.sort_values(by=["probes_filename", parameter], inplace=True)
    validations_df.to_csv(
        "datasets/ploted_metrics_csv/{}_{}.csv".format(
            campaign_name, parameter),
        sep='\t',
        encoding='utf-8')

    plot_campaign_statistics_comparison(validations_df,
                                        campaign_name,
                                        parameter)


root_campaign_name_prefix = "North-Central_20230410"
root_servers_ip_directions = [
    "198.41.0.4",
    "199.9.14.201",
    "192.33.4.12",
    "199.7.91.13",
    "192.203.230.10",
    "192.5.5.241",
    "192.112.36.4",
    "198.97.190.53",
    "192.36.148.17",
    "192.58.128.30",
    "193.0.14.129",
    "199.7.83.42",
    "202.12.27.33"]
cloudfare_campaign_name_prefix = "Europe_countries_20230413"
cloudfare_servers_ip_directions = [
    "104.16.123.96"
]

campaign_name_prefix = cloudfare_campaign_name_prefix
servers_ip_directions = cloudfare_servers_ip_directions

compare_campaign_statistics("North-Central_20230410_198.41.0.4",
                            parameter="alpha")
compare_campaign_statistics("North-Central_20230410_198.41.0.4",
                            parameter="threshold")

'''
for ip in servers_ip_directions:
    campaign_name_complete = "{}_{}".format(campaign_name_prefix, ip)
    csv_metrics_files = get_list_files_in_path("datasets/ploted_metrics_csv/")

    #compare_campaign_statistics(campaign_name_complete, "alpha")
    #compare_campaign_statistics(campaign_name_complete, "threshold")

    for csv_metrics_file in csv_metrics_files:
        metrics_df = pd.read_csv(
            "datasets/ploted_metrics_csv/" + csv_metrics_file,
            sep="\t")
        plot_campaign_statistics_comparison(
            validations_df=metrics_df,
            campaign_name=campaign_name_complete,
            parameter="alpha")
        plot_campaign_statistics_comparison(
            validations_df=metrics_df,
            campaign_name=campaign_name_complete,
            parameter="threshold")
'''
