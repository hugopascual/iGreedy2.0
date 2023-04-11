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
                                        campaign_name: str):
    alpha_unique_values = validations_df["alpha"].unique()
    alpha_unique_values.sort()
    print(alpha_unique_values)
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
            x=alpha_unique_values,
            y=validations_df.loc[validations_df["probes_filename"]
                                 == probes_filename]["accuracy"],
            name=probes_filename),
                         row=1, col=1)
    # Add precision subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=alpha_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["precision"],
            name=probes_filename),
                        row=1, col=2)
    # Add recall subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=alpha_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["recall"],
            name=probes_filename),
                        row=2, col=1)
    # Add F1 subplot
    for probes_filename in probes_filename_unique_values:
        figure.add_trace(go.Scatter(
            x=alpha_unique_values,
            y=validations_df.loc[
                validations_df["probes_filename"] == probes_filename]
            ["f1"],
            name=probes_filename),
                        row=2, col=2)
    figure.update_layout(title_text=campaign_name)
    figure.show()


def compare_campaign_statistics(campaign_name: str):
    campaign_filepath = GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH + \
                        campaign_name + "/"
    validations_list = get_list_files_in_path(campaign_filepath)

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
    validations_df.sort_values(by=["probes_filename", "alpha"], inplace=True)
    validations_df.to_csv(
        "datasets/ploted_metrics_csv/{}.csv".format(campaign_name),
        sep='\t',
        encoding='utf-8')
    plot_campaign_statistics_comparison(validations_df, campaign_name)

'''
campaign_name_prefix = "North-Central_20230410"
root_servers_ip_directions = [
    "198.41.0.4",
    #"199.9.14.201",
    "192.33.4.12",
    "199.7.91.13",
    "192.203.230.10",
    "192.5.5.241",
    #"192.112.36.4",
    "198.97.190.53",
    "192.36.148.17",
    "192.58.128.30",
    "193.0.14.129",
    "199.7.83.42",
    "202.12.27.33"]

for ip in root_servers_ip_directions:
    campaign_name_complete = "{}_{}".format(campaign_name_prefix, ip)
    compare_campaign_statistics(campaign_name_complete)
'''

compare_campaign_statistics("North-Central_20230410_198.41.0.4")
