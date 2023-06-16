#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH
)


def plot_grafics_aggregate():
    aggregation_df = pd.read_csv(
        HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
        "aggregation_results.csv",
        sep=","
    )

    aggregation_df.sort_values(
        by=["moment_of_campaign", "validation"],
        inplace=True
    )

    moment_of_campaign_list = aggregation_df["moment_of_campaign"].unique()
    validation_list = aggregation_df["validation"].unique()

    line_colors_dict = dict(zip(
        validation_list,
        ["red", "green", "blue", "magenta"]
    ))

    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=["Positives", "Negatives", "Indeterminates"])

    for validation in validation_list:
        figure.add_trace(go.Scatter(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation
            ]["country_positives"],
            line_color=line_colors_dict[validation],
            name=validation,
            legendgroup=validation
        ), row=1, col=1)

        figure.add_trace(go.Scatter(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation
                ]["country_negatives"],
            line_color=line_colors_dict[validation],
            name=validation,
            legendgroup=validation,
            showlegend=False
        ), row=1, col=2)

        figure.add_trace(go.Scatter(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation
                ]["country_indeterminates"],
            line_color=line_colors_dict[validation],
            name=validation,
            legendgroup=validation,
            showlegend=False
        ), row=2, col=1)

    figure.show()

def plat_grffic_by_country(country_code: str):
    return


plot_grafics_aggregate()
