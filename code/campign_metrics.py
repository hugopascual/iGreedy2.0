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


def plot_campaign_statistics_comparison(validations_df: pd.DataFrame):
    alpha_unique_values = validations_df["alpha"].unique()
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
    plot_campaign_statistics_comparison(validations_df)


compare_campaign_statistics("20230408_192.5.5.241")
