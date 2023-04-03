#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
import plotly.express as px
# internal modules imports
from utils.constants import (
    GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file,
    get_list_files_in_path
)


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
        row_to_insert = {

        }
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

    plot = px.line(validations_df,
                   x="alpha",
                   y="accuracy",
                   color='probes_filename')
    plot.update_layout(
        title="Metrics of {} in relation to alpha and number of probes"
        .format("accuracy"))
    plot.show()